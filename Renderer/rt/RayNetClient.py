from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import platform
import os
import grpc
import time
import logging

import sys
from protocolimpls import render_pb2_grpc
from protocolimpls import render_pb2

class CredentialHelper(object):
    def __init__(self):
        super().__init__()

    def getCredentials(key: str, cert:str) -> dict:

        credentials = {}
        with open(file='raynetca.crt', mode='rb') as rootca:
            credentials['rootca'] = rootca.read()

        with open(file=key, mode='rb') as key:
            credentials['key'] = key.read()

        with open(file=cert, mode='rb') as cert:
            credentials['cert'] = cert.read()
        

        return credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_tracer_module_path():
    cwd = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(cwd, 'bin')
    if not os.path.isdir(bin_dir):
        logging.error(f"Bin directory not found at {bin_dir}")
        sys.exit(1)
    
    tracer_binary = 'TracerModule'
    if platform.system() == 'Windows':
        tracer_binary += '.exe'
    
    tracer_path = os.path.join(bin_dir, tracer_binary)
    if not os.path.isfile(tracer_path):
        logging.error(f"TracerModule binary not found at {tracer_path}")
        sys.exit(1)
    
    return os.path.abspath(tracer_path)  # Ensure absolute path


def download_scene(stub):
    """Download the scene file from the server."""
    try:
        response = stub.GrabScene(render_pb2.GetCurrentSceneRequest())
        if response.scene_data:
            scene_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scene.nff')
            with open(scene_path, 'wb') as scene_file:
                scene_file.write(response.scene_data)
            logging.info(f"Scene data downloaded and saved to {scene_path}")
            return os.path.abspath(scene_path)  # Ensure absolute path
        else:
            logging.error("No scene data received from the server.")
            return None
    except grpc.RpcError as e:
        logging.error(f"gRPC error while grabbing scene: {e}")
        return None
    

def process_job(stub, tracer_path, scene_path, job):
    """Process a single rendering job."""
    try:
        xbegin = int(job.image_coordinates_to_render.lower_left.x)
        ybegin = int(job.image_coordinates_to_render.lower_left.y)
        xend = int(job.image_coordinates_to_render.upper_right.x)
        yend = int(job.image_coordinates_to_render.upper_right.y)
        
        logging.info(f"Received Job ID {job.job_id}: Rendering from ({xbegin}, {ybegin}) to ({xend}, {yend})")
        
        # Define absolute path for chunk.temp
        chunk_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{job.job_id}_chunk-{xbegin}-{ybegin}-{xend}-{yend}.temp")
        
        # Ensure any existing chunk.temp is removed before rendering
        if os.path.exists(chunk_path):
            os.remove(chunk_path)
            logging.debug(f"Existing chunk.temp removed before rendering.")

        # Execute the tracer module and capture stdout and stderr
        command = [tracer_path, scene_path, str(xbegin), str(xend), str(ybegin), str(yend)]
        logging.debug(f"Executing command: {' '.join(command)}")
        
        start_time = time.time()
        result = subprocess.run(
            [tracer_path, scene_path, chunk_path, str(xbegin), str(xend), str(ybegin), str(yend)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        elapsed_time = time.time() - start_time
        logging.info(f"Rendering completed for Job ID {job.job_id} in {elapsed_time:.2f} seconds")
        logging.debug(f"TracerModule stdout for Job ID {job.job_id}: {result.stdout}")
        if result.stderr:
            logging.warning(f"TracerModule stderr for Job ID {job.job_id}: {result.stderr}")
        
        # Verify that chunk.temp was created
        if not os.path.isfile(chunk_path):
            logging.error(f"Rendered chunk not found at {chunk_path}")
            return
        
        with open(chunk_path, 'rb') as chunk_file:
            render_chunk = chunk_file.read()
        
        # Calculate pixels rendered
        pixels_rendered = (xend - xbegin) * (yend - ybegin)
        
        # Prepare JobCompleteRequest
        job_complete = render_pb2.JobCompleteRequest(
            render_chunk=render_chunk,
            job_id=job.job_id,
            stats=render_pb2.ComputationStatistics(
                time_seconds=elapsed_time,
                pixels_rendered=pixels_rendered
            )
        )
        
        # Send JobComplete to the server
        response = stub.JobComplete(job_complete)
        if response.acknowledged:
            logging.info(f"Job ID {job.job_id} completion acknowledged by server.")
        else:
            logging.warning(f"Job ID {job.job_id} completion not acknowledged by server.")
        
        # Remove the temporary chunk file
        os.remove(chunk_path)
        logging.debug(f"Temporary chunk file {chunk_path} removed.")
        
    except subprocess.CalledProcessError as e:
        logging.error(
            f"Error executing TracerModule for Job ID {job.job_id}: "
            f"Command '{e.cmd}' exited with return code {e.returncode}"
        )
        logging.error(f"TracerModule stderr: {e.stderr}")
    except grpc.RpcError as e:
        logging.error(f"gRPC error while completing Job ID {job.job_id}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error while processing Job ID {job.job_id}: {e}")


def startup():
    """Main function to start the RayNet client."""
    tracer_path = get_tracer_module_path()

    # creds = CredentialHelper.getCredentials('raynetclient.key', 'raynetclient.crt')

    # credentials = grpc.ssl_channel_credentials(root_certificates=creds['rootca'], private_key=creds['key'], certificate_chain=creds['cert'])
    # connection = grpc.secure_channel(target='localhost:50051', credentials=credentials, options=[('grpc.ssl_target_name_override','localhost')])
    
    # Establish gRPC connection to the RenderServer
    server_address = "localhost:50051"  # Update if the server is on a different host
    logging.info(f"Connecting to RenderServer at {server_address}...")
    
    try:
        channel = grpc.insecure_channel(server_address)
        stub = render_pb2_grpc.RenderServiceStub(channel)
        # Wait for the channel to be ready
        grpc.channel_ready_future(channel).result(timeout=10)
        logging.info("Connected to RenderServer successfully.")
    except grpc.FutureTimeoutError:
        logging.error(f"Could not connect to server at {server_address}. Exiting.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error while connecting to server: {e}")
        sys.exit(1)
    
    # Download the scene file once
    scene_path = download_scene(stub)
    if not scene_path:
        logging.error("Failed to download scene. Exiting.")
        sys.exit(1)
    
    # Define the number of worker threads
    max_workers = 4  # Adjust based on your system's capabilities
    
    # Create a thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        try:
            while True:
                try:
                    job_request = render_pb2.GetJobRequest(project_id=0)  # project_id can be modified as needed
                    job_response = stub.GetJob(job_request)
                    
                    if job_response.job_id > 0:
                        # Submit job to the thread pool
                        future = executor.submit(process_job, stub, tracer_path, scene_path, job_response)
                        futures.append(future)
                    else:
                        logging.info("No jobs available. Waiting for new jobs...")
                        time.sleep(5)  # Wait before polling again
                except grpc.RpcError as e:
                    logging.error(f"gRPC error during GetJob: {e}")
                    time.sleep(5)  # Wait before retrying
                except Exception as e:
                    logging.error(f"Unexpected error in main loop: {e}")
                    time.sleep(5)  # Wait before retrying
            
            # Optionally, handle completed futures
            for future in as_completed(futures):
                exception = future.exception()
                if exception:
                    logging.error(f"Job processing raised an exception: {exception}")
        except KeyboardInterrupt:
            logging.info("RayNet client is shutting down gracefully.")

if __name__ == '__main__':
    startup()

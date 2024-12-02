import time
from protocolimpls import render_pb2_grpc
from protocolimpls import render_pb2

import grpc
import os

from concurrent import futures
import threading
from PIL import Image
import io

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue
import logging


jobsExpected = 0
jobsCompleted = 0
jobQueue = queue.Queue()


resultLock = threading.Lock()
jobQueueLock = threading.Lock()
resultMap = {}
scene_data_global = None

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

def createJobs(scene_data):
    global jobsExpected, scene_data_global
    horizontalResolution = 0
    verticalResolution = 0
    logging.info('Beginning scene data parsing...')
    scene_data_global = scene_data

    try:
        scene_text = scene_data.decode('ascii')
        lines = scene_text.splitlines()
        logging.info('Ingested %d lines of input data', len(lines))
        for line in lines:
            logging.debug("Parsing line: %s", line)
            parsed = line.strip().split()
            if len(parsed) > 0 and parsed[0].lower() == 'resolution':
                try:
                    horizontalResolution = int(parsed[1])
                    verticalResolution = int(parsed[2])
                    logging.info('Parsed resolution: %dx%d', horizontalResolution, verticalResolution)
                except ValueError as e:
                    logging.error('Invalid resolution values: %s', e)
                    break
                break
        if horizontalResolution == 0 or verticalResolution == 0:
            logging.error('No valid resolution data found in scene file.')
            return
        logging.info('Resolution set to %dx%d', horizontalResolution, verticalResolution)
    except Exception as e:
        logging.error("An error occurred while parsing scene data: %s", e)
        return

    try:
        with open(file="output.ppm", mode='wb') as ppm:
            ppm.write(b'P6\n')
            ppm.write(f'{horizontalResolution} {verticalResolution}\n'.encode('ascii'))
            ppm.write(b'255\n')
        logging.info('PPM header written successfully.')
    except Exception as e:
        logging.error('Error writing PPM header: %s', e)
        return

    logging.info('Creating jobs...')
    jobsExpected = verticalResolution
    jobCounter = 0
    for scanline in range(verticalResolution):
        rectStart = render_pb2.Coordinate(x=0, y=scanline)
        # **Ensure yend does not exceed verticalResolution**
        yend = scanline + 1 if (scanline + 1) <= verticalResolution else verticalResolution
        rectEnd = render_pb2.Coordinate(x=horizontalResolution, y=yend)
        rect = render_pb2.Rectangle(lower_left=rectStart, upper_right=rectEnd)
        jobCounter += 1
        job = render_pb2.GetJobResponse(image_coordinates_to_render=rect, job_id=jobCounter)
        with jobQueueLock:
            jobQueue.put(job)
    logging.info('Queued %d jobs.', jobCounter)


def cleanupServerResources():
    global jobsCompleted, jobsExpected, scene_data_global
    jobsCompleted = 0
    jobsExpected = 0
    resultMap.clear()
    scene_data_global = None
    logging.info('Server resources have been cleaned up.')


def stitch():
    global jobsExpected, jobsCompleted
    while True:
        with resultLock:
            if jobsCompleted == jobsExpected and jobsExpected != 0:
                logging.info('All chunks received: %d', len(resultMap.keys()))
                # Write the chunks in order based on job_id
                with open("output.ppm", 'ab') as ppm:
                    for job_id in sorted(resultMap.keys()):
                        ppm.write(resultMap[job_id])
                logging.info("An image has been rendered and saved to output.ppm")
                
                # Convert PPM to PNG
                try:
                    with open("output.ppm", 'rb') as ppm_file:
                        ppm_data = ppm_file.read()
                    image = Image.open(io.BytesIO(ppm_data))
                    image.save("output.png", "PNG")
                    logging.info("Converted output.ppm to output.png successfully.")
                except Exception as e:
                    logging.error("Error converting PPM to PNG: %s", e)
                
                cleanupServerResources()
                break
        time.sleep(1)


class RenderServiceServicer(render_pb2_grpc.RenderServiceServicer):
    def __init__(self):
        super().__init__()

    def GetJob(self, request, context):
        with jobQueueLock:
            if not jobQueue.empty():
                job = jobQueue.get()
                logging.info('Assigned job ID %d to a client', job.job_id)
                return job
            else:
                # No jobs available
                return render_pb2.GetJobResponse(job_id=0)

    def JobComplete(self, request, context):
        logging.info('Received rendered chunk for job ID %d', request.job_id)
        with resultLock:
            global jobsCompleted
            jobsCompleted += 1
            resultMap[request.job_id] = request.render_chunk
        return render_pb2.JobCompleteResponse(acknowledged=True)

    def Heartbeat(self, request, context):
        return render_pb2.HeartbeatResponse(alive=True)

    def GrabScene(self, request, context):
        # Send the scene data stored in memory
        if scene_data_global:
            data = scene_data_global
            logging.info('Providing scene data to client')
        else:
            data = b''
            logging.warning('No scene data available to send to client')
        return render_pb2.GetCurrentSceneResponse(scene_data=data)

    def UploadScene(self, request, context):
        try:
            scene_data = request.scene_data
            if not scene_data:
                raise ValueError("No scene data provided")
            logging.info('Received scene data of size %d bytes', len(scene_data))
            createJobs(scene_data)
            threading.Thread(target=stitch, daemon=True).start()
            return render_pb2.UploadSceneResponse(success=True, message='Scene data uploaded and jobs created.')
        except Exception as e:
            logging.error('Error uploading scene data: %s', e)
            return render_pb2.UploadSceneResponse(success=False, message=str(e))
        
    def DownloadRenderedImage(self, request, context):
        # Check if rendering is complete
        with resultLock:
            rendering_complete = (jobsExpected > 0) and (jobsCompleted == jobsExpected)
        # Prepare render stats
        with resultLock, jobQueueLock:
            job_ids_pending = [job.job_id for job in list(jobQueue.queue)]
            job_ids_completed = list(resultMap.keys())
            stats = render_pb2.RenderStatsResponse(
                jobs_expected=jobsExpected,
                jobs_completed=jobsCompleted,
                job_ids_pending=job_ids_pending,
                job_ids_completed=job_ids_completed
            )
        image_data = b''
        if rendering_complete:
            try:
                # Read the PNG image instead of PPM
                with open('output.png', 'rb') as img_file:
                    image_data = img_file.read()
                logging.info('Rendered image has been read successfully. Size: %d bytes.', len(image_data))
            except Exception as e:
                logging.error('Error reading rendered image: %s', e)
                rendering_complete = False  # Cannot read image
        else:
            logging.info('Rendering is not yet complete.')
        return render_pb2.DownloadRenderedImageResponse(
            image_data=image_data,
            rendering_complete=rendering_complete
        )
    
    def GetRenderStats(self, request, context):
        logging.info('Received GetRenderStats request.')

        with resultLock, jobQueueLock:
            job_ids_pending = [job.job_id for job in list(jobQueue.queue)]
            job_ids_completed = list(resultMap.keys())
            stats = render_pb2.RenderStatsResponse(
                jobs_expected=jobsExpected,
                jobs_completed=jobsCompleted,
                job_ids_pending=job_ids_pending,
                job_ids_completed=job_ids_completed
            )
        
        logging.info('Returning render stats: %s', stats)
        return stats


def bootstrap():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=6, thread_name_prefix='gRPC_Render_Server'))
    render_pb2_grpc.add_RenderServiceServicer_to_server(RenderServiceServicer(), server)
    
    # creds = CredentialHelper.getCredentials('raynetserver.key', 'raynetserver.crt')
    # credentials = grpc.ssl_server_credentials(private_key_certificate_chain_pairs=[(creds['key'], creds['cert'])], root_certificates=creds['rootca'], require_client_auth=True)
    
    # renderServer.add_secure_port(address='localhost:50051', server_credentials=credentials)
    server.add_insecure_port("0.0.0.0:50051")

    server.start()
    logging.info("Coordination Server is now listening on port 50051")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop(0)
        logging.info("Coordination Server has been terminated.")


if __name__ == '__main__':
    bootstrap()

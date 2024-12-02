import time
from protocolimpls import render_pb2_grpc
from protocolimpls import render_pb2

import grpc
import os

from concurrent import futures
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue
import logging


jobsExpected = 0
jobsCompleted = 0
jobQueue = queue.Queue(10)


resultLock = threading.Lock()
resultMap = {}
SCENEPATH = "scene_file"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

def createJobs(filename):

    global jobsExpected
    horizontalResolution = 0
    verticalResolution = 0
    logging.info('Beginning scene file parsing...')
    print("opening: ", filename)
    
    try:
        with open(file=filename, mode='r', encoding='ascii') as nff:
            lines = nff.readlines()
            print('ingested ', len(lines), 'lines of input file')
            for line in lines:

                print(line)
                parsed = line.strip().split()
                
                if(len(parsed) > 0 and parsed[0] == 'resolution'):
                    horizontalResolution = int(parsed[1])
                    verticalResolution = int(parsed[2])
                    break
            logging.info('Resolution data found')
    except FileNotFoundError:
        print("File not found!")
    except PermissionError:
        print("Permission denied!")
    except Exception as e:
        print("An error occurred:", e)

    with open(file="output.ppm", mode='w') as ppm:
        ppm.writelines(['P6\n', str(horizontalResolution) + ' ' + str(verticalResolution) + '\n', '255\n'])

    logging.info('Creating jobs...')
    jobsExpected = verticalResolution
    jobCounter = 0
    for scanline in range(0, verticalResolution):
        
        rectStart = render_pb2.Coordinate(x=0, y=scanline)
        rectEnd = render_pb2.Coordinate(x=horizontalResolution, y=(scanline + 1))
        rect = render_pb2.Rectangle(lower_left=rectStart, upper_right=rectEnd)
        jobCounter += 1
        jobQueue.put(render_pb2.GetJobResponse(image_coordinates_to_render=rect, job_id=jobCounter))
        

def cleanupServerResources():
    global jobsCompleted, jobsExpected
    jobsCompleted = 0 
    jobsExpected = 0
    resultMap.clear()

    try:
        sceneFiles = os.listdir('scene_file')
        for f in sceneFiles:
            fp = os.path.join('scene_file', f)
            os.remove(fp)
            logging.info('removed scene file data')
    except:
        logging.error('unable to clear scene file data')


def stitch():

    while True:
        if(jobsCompleted == jobsExpected):
            print('all chunks received: ' + str(len(resultMap.keys())))
            for chunk in resultMap.keys():
                with open("output.ppm", 'ab') as ppm:
                    ppm.write(resultMap.get(chunk))
                
            break
        else:
            print('delaying')
            time.sleep(1)

    # ffmpeg.input('output.ppm').output("output.png", pix_fmt='rgb24').run()
    logging.info("An image has been rendered")
    cleanupServerResources()


class FilePlacementHandler(FileSystemEventHandler):

    def on_created(self, event):
        if not event.is_directory:

            while os.path.getsize(event.src_path) == 0:
                print('waiting for file transfer before processing')
                time.sleep(1)


            createJobs(event.src_path)
            stitch()




class RenderServiceServicer(render_pb2_grpc.RenderServiceServicer):
    def __init__(self) -> None:
        super().__init__()

    

    def GetJob(self, request, context):
        
        return jobQueue.get()


    def JobComplete(self, request, context):

        logging.warning('Received scene chunk with id=' + str(request.job_id))

        

        with resultLock:
            global jobsCompleted
            jobsCompleted += 1
            chunk = request.render_chunk
            resultMap[request.job_id] = chunk
        
        return render_pb2.JobCompleteResponse(acknowledged=True)
    

    def Heartbeat(self, request, context):
        return render_pb2.HeartbeatResponse(alive=True)
    
    def GrabScene(self, request, context):

        data = None
        with open(os.path.join(SCENEPATH, os.listdir(SCENEPATH)[0]), 'rb') as scene:
            data = scene.read()

        return render_pb2.GetCurrentSceneResponse(scene_data=data)


    
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



def bootstrap():
    renderServer = grpc.server(futures.ThreadPoolExecutor(max_workers=6, thread_name_prefix='gRPC_Render_Server'))
    render_pb2_grpc.add_RenderServiceServicer_to_server(RenderServiceServicer(), renderServer)
    
    # creds = CredentialHelper.getCredentials('raynetserver.key', 'raynetserver.crt')
    # credentials = grpc.ssl_server_credentials(private_key_certificate_chain_pairs=[(creds['key'], creds['cert'])], root_certificates=creds['rootca'], require_client_auth=True)
    
    # renderServer.add_secure_port(address='localhost:50051', server_credentials=credentials)
    renderServer.add_insecure_port("0.0.0.0:50051")

    renderServer.start()
    logging.warning("Coordination Server now listening on port 50051")
    
    fsObserver = Observer()
    fsObserver.schedule(event_handler=FilePlacementHandler(), path=os.path.join(os.getcwd(), SCENEPATH), recursive=False)
    fsObserver.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        fsObserver.stop()
    

    renderServer.wait_for_termination()
    logging.warning("Terminating Coordination Server")
    fsObserver.join()
if __name__ == '__main__':
    bootstrap()

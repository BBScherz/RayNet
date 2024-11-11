import time
from protocolimpls import render_pb2_grpc
from protocolimpls import render_pb2

import grpc
import os

from concurrent import futures

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import queue

jobsExpected = 0
jobsCompleted = 0
jobQueue = queue.Queue(10)
resultList = []
# resultQueue = queue.Queue()
SCENEPATH = "scene_file"


def createJobs(filename):

    global jobsExpected
    horizontalResolution = 0
    verticalResolution = 0

    with open(file=filename, mode='r') as nff:
        print("opening file")
        for line in nff:
            parsed = line.strip().split()

            if(len(parsed) > 0 and parsed[0] == 'resolution'):
                horizontalResolution = int(parsed[1])
                verticalResolution = int(parsed[2])
                break


    with open(file="output.ppm", mode='w') as ppm:
        ppm.writelines(['P6\n', str(horizontalResolution) + ' ' + str(verticalResolution) + '\n', '255\n'])


    jobsExpected = verticalResolution
    jobCounter = 0
    for scanline in range(0, verticalResolution):
        
        print('creating jobs for y=', scanline)
            
        rectStart = render_pb2.Coordinate(x=0, y=scanline)
        rectEnd = render_pb2.Coordinate(x=horizontalResolution, y=(scanline + 1))
        rect = render_pb2.Rectangle(lower_left=rectStart, upper_right=rectEnd)
        jobCounter += 1
        jobQueue.put(render_pb2.GetJobResponse(image_coordinates_to_render=rect, job_id=jobCounter))



def stitch():

    
    while True:
        if(jobsCompleted == jobsExpected):
            print('all chunks received: ' + str(len(resultList)))
            for chunk in resultList:
                with open("output.ppm", 'ab') as ppm:
                    # print('appending chunk...')
                    ppm.write(chunk)
                
            break
        else:
            print('delaying')
            time.sleep(1)

    # while True:
    #     chunk = resultQueue.get()
    #     with open("output.ppm", 'ab') as ppm:
    #            print('appending chunk...')
    #            ppm.write(chunk)
    #     if resultQueue.qsize() == 0:
    #         break

    print("image stitched!!")


class FilePlacementHandler(FileSystemEventHandler):

    def on_created(self, event):
        if not event.is_directory:
            print("Beginning job creation!")
            createJobs(event.src_path)
            stitch()







class RenderServiceServicer(render_pb2_grpc.RenderServiceServicer):
    def __init__(self) -> None:
        super().__init__()

    

    def GetJob(self, request, context):
        
        return jobQueue.get()


    def JobComplete(self, request, context):

        print('result received!')
        global jobsCompleted
        jobsCompleted += 1
        chunk = request.render_chunk
        resultList.insert(request.job_id, chunk)
        
        # resultQueue.put(chunk)
        

        return render_pb2.JobCompleteResponse(acknowledged=True)





def bootstrap():
    renderServer = grpc.server(futures.ThreadPoolExecutor(max_workers=6, thread_name_prefix='gRPC_Render_Server'))
    render_pb2_grpc.add_RenderServiceServicer_to_server(RenderServiceServicer(), renderServer)
    renderServer.add_insecure_port("127.0.0.1:50505")

    renderServer.start()
    print("server is up!")
    
    fsObserver = Observer()
    fsObserver.schedule(event_handler=FilePlacementHandler(), path=os.path.join(os.getcwd(), SCENEPATH), recursive=False)
    fsObserver.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        fsObserver.stop()
    

    renderServer.wait_for_termination()
    print("server shutdown")
    fsObserver.join()
if __name__ == '__main__':
    bootstrap()
import subprocess
import platform
import os
import grpc
import time

import sys
# from ..gRPCServer.protocolimpls import render_pb2, render_pb2_grpc
sys.path.insert(0,'../gRPCServer/')
from protocolimpls import render_pb2_grpc # type: ignore
from protocolimpls import render_pb2 # type: ignore


def startup():
    try:
        cwd = os.path.dirname(__file__)
        print(cwd)
        os.chdir(os.path.join(cwd, 'bin'))
        

    except:
        print('failed to set current directory')
    
    bin = os.path.join(os.getcwd(), 'TracerModule')

    binaryTag = '.exe' if platform.system() == 'Windows' else ''
    
    

    connection = grpc.insecure_channel("127.0.0.1:50505")
    methodStub = render_pb2_grpc.RenderServiceStub(connection)
    while True:
        currentJob = methodStub.GetJob(render_pb2.GetJobRequest(project_id=0))
        if currentJob != None:
            print('Starting', bin + binaryTag)
            xbegin = currentJob.image_coordinates_to_render.lower_left.x
            ybegin = currentJob.image_coordinates_to_render.lower_left.y
            xend = currentJob.image_coordinates_to_render.upper_right.x
            yend = currentJob.image_coordinates_to_render.upper_right.y

            
            startTime = time.time()
            startupTask = subprocess.run([bin + binaryTag, 'teapot-3.nff', str(int(xbegin)), str(int(xend)), str(int(ybegin)), str(int(yend))], text=True, capture_output=True)
            startupTask.check_returncode()
            elapsed = int(time.time() - startTime)
            
            print(f"Finished rendering ({xbegin},{ybegin}) to ({xend},{yend})")
            time.sleep(0.25)
            with open(file=os.path.join(os.getcwd(), "chunk.temp"), mode='rb') as chunk:
                data = chunk.read()
                print(data)
                pixelsRendered = (xend - xbegin) * (yend - ybegin)
                completed = render_pb2.JobCompleteRequest(render_chunk=data, job_id=currentJob.job_id, stats=render_pb2.ComputationStatistics(time_seconds=elapsed, pixels_rendered=int(pixelsRendered)))
                methodStub.JobComplete(completed)
            os.remove(path=os.path.join(os.getcwd(), "chunk.temp"))
                

            

            
        

if __name__ == '__main__':
    startup()
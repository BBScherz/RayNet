import subprocess
import platform
import os
import grpc
import time

import sys
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

            print(os.getcwd())
            startupTask = subprocess.run([bin + binaryTag, '4k-teapot-3.nff', str(int(xbegin)), str(int(xend)), str(int(ybegin)), str(int(yend))], text=True, capture_output=True)
            startupTask.check_returncode()
            print(startupTask.stdout)
            print(startupTask.stderr)
            # print(f""" from x={xbegin} y={ybegin}  to x={xend} y={yend}""" )
            # time.sleep(3)

            
        

if __name__ == '__main__':
    startup()
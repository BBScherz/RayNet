import subprocess
import platform
import os
import grpc

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
    print(bin + binaryTag)
    # startupTask = subprocess.run([bin + binaryTag], shell=True, capture_output=True, text=True)
    

    connection = grpc.insecure_channel("127.0.0.1:50505")
    methodStub = render_pb2_grpc.RenderServiceStub(connection)
    while True:
        currentJob = methodStub.GetJob(render_pb2.GetJobRequest(project_id=0))
        if currentJob != None:
            print(currentJob)
        

if __name__ == '__main__':
    startup()
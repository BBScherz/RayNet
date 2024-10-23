from protocolimpls.render_pb2_grpc import *
import grpc
from concurrent import futures






class RenderServiceServicer(RenderServiceServicer):
    def __init__(self) -> None:
        super().__init__()

    def GetJob(self, request, context):
        id = request.project_id




def bootstrap():
    renderServer = grpc.server(futures.ThreadPoolExecutor(max_workers=6, thread_name_prefix='gRPC_Render_Server'))
    add_RenderServiceServicer_to_server(RenderServiceServicer(), renderServer)
    renderServer.add_insecure_port("127.0.0.1:50505")

    renderServer.start()
    print("server is up!")
    
    renderServer.wait_for_termination()
    print("server shutdown")

if __name__ == '__main__':
    bootstrap()
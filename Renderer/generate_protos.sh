# to build to protocol implementations for the server
# NOTE: add 'import protocolimpls.render_pb2 as render__pb2' to render_pb2.py post-generation, otherwise will not work
py -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. --pyi_out=. ./protos/render.proto
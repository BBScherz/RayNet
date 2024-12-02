python -m grpc_tools.protoc -I./protos --python_out=. --grpc_python_out=. --pyi_out=. ./protos/render.proto

OS=$(uname)
if [[ "$OS" == "Darwin" ]]; then
  sed -i '' '6i\
from . ' render_pb2_grpc.py
else
  sed -i '6i\from . ' render_pb2_grpc.py
fi

for dir in gRPCServer/protocolimpls rt/protocolimpls ../Web/protocolimpls; do
    for out_file in render_pb2_grpc.py render_pb2.py render_pb2.pyi; do
        rm -rf "$dir/$out_file"
        cp $out_file "$dir/"
    done
done

rm -rf render_pb2_grpc.py render_pb2.py render_pb2.pyi
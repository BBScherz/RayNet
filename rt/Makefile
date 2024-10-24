CXX = g++
#add -O3 for optimizations
CXXFLAGS = -Wall  -O3 -g -I$(EIGEN_PATH)
CXXPARALLELFLAGS = -fopenmp
EIGEN_PATH = lib/eigen-3.4.0


TracerModule: scene/* objects/Object.h  main.cpp
		$(CXX) $(CXXFLAGS) $(CXXPARALLELFLAGS) util/* scene/* objects/Object.h  main.cpp -o bin/TracerModule

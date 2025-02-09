#include<iostream>
#include <chrono>

#ifdef _OPENMP
#include <omp.h>
#endif

#include "scene/SceneFileParser.h"
#include "scene/Scene.h"




using namespace std;

int main(int argc, char* argv[]){
    

    if(argc != 7){
        cerr << "Error starting TracerModule.  Exiting..." << endl;
        exit(-1);
    }

    string file = argv[1];
    string outChunkFile = argv[2];
    int beginx = atoi(argv[3]);
    int endx = atoi(argv[4]);
    int beginy = atoi(argv[5]);
    int endy = atoi(argv[6]);
    cout << beginx << " " << beginy << " " << endx << " " << endy << endl;

    chrono::steady_clock::time_point begin = chrono::steady_clock::now();

    SceneFileParser parser;
    Scene scene = parser.parseSceneFile(file);
    scene.summarize();

    #ifdef _OPENMP
    cout << "Parallelism Enabled" << endl;
    #else
    cout << "Parallelism Disabled" << endl;
    #endif



    
    unsigned char* redneredChunk = scene.trace(beginx, beginy, endx, endy);
    chrono::steady_clock::time_point end = chrono::steady_clock::now();

    cout << "Chunk Rendered: (" << endx - beginx << 'x' << endy - beginy << ")"  << endl;
    cout << "Pixels Rednered: " << (endx - beginx) * (endy - beginy) << endl;
    cout << "Render time (wall): " << chrono::duration_cast<chrono::seconds>(end - begin).count() << "(seconds)" << endl;    


    std::ofstream out(outChunkFile, ios::out | ios::binary);
    out.write(reinterpret_cast<char*>(redneredChunk), (endx - beginx) * (endy - beginy) * 3);
    out.close();
    delete[] redneredChunk;
    
    return 0;
}
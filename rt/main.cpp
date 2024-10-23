#include<iostream>

#ifdef _OPENMP
#include <omp.h>
#endif

#include "scene/SceneFileParser.h"
#include "scene/Scene.h"




using namespace std;

int main(int argc, char* argv[]){
    
    SceneFileParser parser;
    Scene scene = parser.parseSceneFile("4k-teapot-3.nff");
    scene.summarize();

    #ifdef _OPENMP
    cout << "total number of openmp compute devices = " << omp_get_num_devices() << endl;
    #endif


    int beginx = 0;
    int endx = 4096;
    int beginy = 0;
    int endy = 2160;
    unsigned char* redneredChunk = scene.trace(beginx, beginy, endx, endy);
    cout << "Chunk Rendered: (" << endx - beginx << 'x' << endy - beginy << ")"  << endl;

    std::ofstream out("test.ppm", ios::out | ios::binary);
    out<<"P6"<<"\n"<<(endx - beginx)<<" "<<(endy - beginy)<<"\n"<<255<<"\n";
    out.write(reinterpret_cast<char*>(redneredChunk), (endx - beginx) * (endy - beginy) * 3);
    out.close();
    delete[] redneredChunk;
    
    return 0;
}
#ifndef _SCENE_H
#define _SCENE_H

#include <iostream>
#include <vector>

#ifdef _OPENMP
#include <omp.h>
#include <thread>
// #define AVAILABLE_THREADS thread::hardware_concurrency();
#endif

#include "../objects/Object.h"
#include "Camera.h"
#include "Light.h"
using namespace std;

class Scene{

    public:
        Scene();
        ~Scene();
        void summarize();
        unsigned char* trace(int xStart, int yStart, int xEnd, int yEnd);

        int xResolution;
        int yResolution;
        double fov;
        double hither;
        Camera* cam;
        Eigen::Vector3d from;
        Eigen::Vector3d at;
        Eigen::Vector3d up;
        Eigen::Vector3d backdropColor;
        vector<Light> lights;
        vector<Object*> objects;


};

Scene::Scene(){}
Scene::~Scene()
{
 this->objects.clear();   
}


unsigned char* Scene::trace(int xStart, int yStart, int xEnd, int yEnd){

    unsigned char* render = new unsigned char[(xEnd - xStart) * (yEnd - yStart) * 3];
    double sceneDistance = Calculations::sceneBorderWidth(this->fov);
    double pixelWidth =  Calculations::calculatePixelWidth(sceneDistance, this->xResolution);

    double sceneProgress = 0.0;
    double sceneProgressIncrement = 1.0 / ((yEnd - yStart) * (xEnd - xStart));
    #ifdef _OPENMP
    omp_set_dynamic(0);
    const int threadCeiling = thread::hardware_concurrency() / 2;
    #pragma omp parallel for collapse(2) num_threads(threadCeiling)
    #endif
    for(int y = 0; y < yEnd - yStart; y++){
        
        for(int x = 0; x < xEnd - xStart; x++){

                bool anyIntersection = false;
                int superSamples = 8;
                Eigen::Vector3d superSampledColor;
                superSampledColor.setZero();

                
                for(int jitter = 0; jitter < superSamples; jitter++){

                    double minDistance = 0;
                    double maxDistance = INFINITY;
                    Eigen::Vector3d pixelInCameraSpace = Calculations::calculatePixelCenterCoordinates(this->xResolution, this->yResolution, x, y, pixelWidth, sceneDistance, this->hither);
                    Eigen::Vector3d rayDirection = Calculations::pixelCoordinatesToWorldCoordinates(pixelInCameraSpace, this->cam);

                    Ray r(this->from, rayDirection);
                    IntersectionRecord ir;

                    Object* nearest = nullptr;
                    for(Object* obj: objects){

                        if(obj->calculateIntersection(ir, r, minDistance, maxDistance)){

                            if(ir.getIntersectionDistance() < maxDistance){

                                maxDistance = ir.getIntersectionDistance();
                                anyIntersection = true;
                                nearest = obj;
                            }
                        }
                    }

                    if(anyIntersection && nearest != nullptr){
                        int currentDepth = 0;
                        int maxRecursionDepth = 5;
                        Eigen::Vector3d computedColor = nearest->computeCompositeColor(ir, r, lights, objects, backdropColor, currentDepth, maxRecursionDepth);
                        superSampledColor += computedColor;
                    }
                }
                
                
                if(anyIntersection){

                    render[3 * (y * (xEnd - xStart) + x) + 0] = min((superSampledColor[0] / superSamples) * 255, 255.0);
                    render[3 * (y * (xEnd - xStart) + x) + 1] = min((superSampledColor[1] / superSamples) * 255, 255.0);
                    render[3 * (y * (xEnd - xStart) + x) + 2] = min((superSampledColor[2] / superSamples) * 255, 255.0);
                }else{
                    render[3 * (y * (xEnd - xStart) + x) + 0] = this->backdropColor[0] * 255;
                    render[3 * (y * (xEnd - xStart) + x) + 1] = this->backdropColor[1] * 255;
                    render[3 * (y * (xEnd - xStart) + x) + 2] = this->backdropColor[2] * 255;
                }

                

                #pragma omp critical
                {
                sceneProgress += sceneProgressIncrement;
                cout << (sceneProgress * 100) << "%\r" << flush;
                }
        }

    }

    return render;
}








void Scene::summarize(){
    
    cout << "Scene Summary:\n" << endl;
    cout << "Scene backdrop RGB values = " << this->backdropColor[0] << " " << this->backdropColor[1] << " " << this->backdropColor[2];

    cout << "\nScene Viewport:\n------------------" << endl;
    cout << "Horizontal Resolution=" << xResolution << "px" << endl;
    cout << "Vertical Resolution=" << yResolution << "px" << endl;
    cout << "FOV Angle=" << fov << endl;

    cout << "\nScene Lights:\n------------------" << endl;
    for (long unsigned i = 0; i < lights.size(); i++)
    {
        cout << "Light " << i << endl;
        cout << "position=" << lights.at(i).xyz[0] << " " << lights.at(i).xyz[1] << " " << lights.at(i).xyz[2] << endl;;
        cout << "RGB values=" << lights.at(i).rgb[0] << " " << lights.at(i).rgb[1] << " " << lights.at(i).rgb[2] << endl;;
        cout << endl;
    }

    cout << "\nPolygons Parsed=" << this->objects.size() << endl;
    
}


#endif
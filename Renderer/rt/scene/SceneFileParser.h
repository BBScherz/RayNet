#ifndef _SCENEFILEPARSER_H
#define _SCENEFILEPARSER_H

#include <iostream>
#include <filesystem>
#include <fstream>
#include <string>
#include "Scene.h"
#include "../objects/Poly.h"

using namespace std;


//used to identify which area the parser is currently reading
enum descriptorIdentifier{
    BACKDROP = 'b',
    VIEWPORT = 'v',
    LIGHT = 'l',
    FILL = 'f',
    POLYGON = 'p'
};



/**
 * reads in the downloaded scene file and loads it into memory for use later
 */
class SceneFileParser{

    private:
        Material currentMaterial;
        void clearStreamMacro(stringstream& s);

    public:
        SceneFileParser(){}
        Scene parseSceneFile(string file);
};



void SceneFileParser::clearStreamMacro(stringstream& s){
    s.str("");
    s.clear();
}



/**
 * Parses out the downloaded scene description file
 * Will return a scene description object
 */
Scene SceneFileParser::parseSceneFile(string file){

    string path = "../file/" + file;
    string currentSceneLine = "";
    Scene scene;

    //attempt to load the scene
    try
    {
        ifstream sceneFile(path);
        if(sceneFile.is_open()){

            /**
             * The .NFF scene description language is standardized.  If the file is not formatted properly, fail fast
             */
            cout << "Beginning parsing of scene data from " << file << endl;

            string id = "";
            stringstream dataStream;
            while (getline(sceneFile, currentSceneLine))
            {
                switch (currentSceneLine.front())
                {
                    // parses and stores the scene background image
                    case BACKDROP:
                    {    
                        dataStream << currentSceneLine;
                        dataStream >> id >> scene.backdropColor[0] >> scene.backdropColor[1] >> scene.backdropColor[2];
                        clearStreamMacro(dataStream);
                        id = "";
                        break;

                    }

                    // parses scene information used during tracing
                    case VIEWPORT:
                    {

                        const int VIEWDATA = 6;
                        int viewDataSection = 0;
                        

                        // there are six pieces of data required for the viewport
                        while(viewDataSection < VIEWDATA){

                            getline(sceneFile, currentSceneLine);
                            string viewDataKey = currentSceneLine.substr(0, currentSceneLine.find_first_of(' '));
                            
                            if(viewDataKey == "from"){

                                Eigen::Vector3d fromVector;
                                dataStream << currentSceneLine;
                                dataStream >> id >> fromVector[0] >> fromVector[1] >> fromVector[2];
                                scene.from = fromVector;
                                viewDataSection++;
                                
                            }else if (viewDataKey == "at")
                            {
                                Eigen::Vector3d atVector;
                                dataStream << currentSceneLine;
                                dataStream >> id >> atVector[0] >> atVector[1] >> atVector[2];
                                scene.at = atVector;
                                viewDataSection++;

                            }else if (viewDataKey == "up")
                            {
                                Eigen::Vector3d upVector;
                                dataStream << currentSceneLine;
                                dataStream >> id >> upVector[0] >> upVector[1] >> upVector[2];
                                scene.up = upVector;
                                viewDataSection++;
                                
                            }else if (viewDataKey == "angle")
                            {
                                double fov;
                                dataStream << currentSceneLine;
                                dataStream >> id >> fov;
                                scene.fov = fov;
                                viewDataSection++;

                            }else if (viewDataKey == "hither")
                            {
                                double hither;
                                dataStream << currentSceneLine;
                                dataStream >> id >> hither;
                                scene.hither = hither;
                                viewDataSection++;

                            }else if (viewDataKey == "resolution")
                            {
                                double xRes;
                                double yRes;
                                dataStream << currentSceneLine;
                                dataStream >> id >> xRes >> yRes;
                                scene.xResolution = xRes;
                                scene.yResolution = yRes;
                                viewDataSection++;
                            }else{
                                cout << "skipping line..." << endl;
                            }
                            
                            clearStreamMacro(dataStream);
                            id = "";
                        }

                        // once viewport data has been parsed, create the scene camera
                        scene.cam = new Camera(scene.from, scene.at, scene.up);


                        break;
                    }

                    // scene lights will always have position, but color is not guaranteed
                    // if data isnt present, they will default to rgb values representing 'white'
                    case LIGHT:
                    {
                        Light l;
                        Eigen::Vector3d xyz;
                        Eigen::Vector3d rgb;
                        dataStream << currentSceneLine;
                        dataStream >> id >> xyz[0] >> xyz[1] >> xyz[2];

                        double colorTest;
                        if(dataStream >> colorTest){
                            rgb[0] = colorTest;
                            dataStream >> rgb[1] >> rgb[2];
                        }else{

                            rgb[0] = 1.0;
                            rgb[1] = 1.0;
                            rgb[2] = 1.0;
                        }

                        l.xyz = xyz;
                        l.rgb = rgb;
                        
                        
                        scene.lights.push_back(l);
                        
                        clearStreamMacro(dataStream);
                        id = "";
                        break;
                    }

                    // parses the current object material data
                    case FILL:
                    {

                        dataStream << currentSceneLine;
                        dataStream >> id >> currentMaterial.__red >> currentMaterial.__green >> currentMaterial.__blue
                                         >> currentMaterial.__diffuseComponent >> currentMaterial.__specularComponent >> currentMaterial.__shine 
                                         >> currentMaterial.__transmittence >> currentMaterial.__refractionIndex;
                        cout << currentMaterial << endl;

                        clearStreamMacro(dataStream);
                        id = "";
                        break;
                    }


                    case POLYGON:
                    {

                        // determine if a polygon's vertices have predefined normal vectors
                        bool polygonalPatch = currentSceneLine.at(1) == 'p';
                        int vertexCount;

                        dataStream << currentSceneLine;
                        dataStream >> id >> vertexCount;

                        /**
                         * Read polygon data and store within the scene's object datastructure
                         * Treat a vertex count of 3 as a standard triangle
                         * Anything greater will be fanned into a series of triangles, similar to modern 3D modeling software exports
                         */
                        Poly* polygon = nullptr;
                        if(vertexCount == 3){

                            polygon = new Poly();
                            int currentVertex = 0;

                            while (currentVertex < vertexCount){
                            
                                getline(sceneFile, currentSceneLine);
                                if(currentSceneLine.front() != '#'){
                                    dataStream << currentSceneLine;
                                    polygon->appendVertex(dataStream, polygonalPatch);
                                    currentVertex++;
                                    clearStreamMacro(dataStream);
                                }
                            }
                            polygon->setMaterial(currentMaterial);
                            Eigen::Vector3d n = Calculations::calculatePolygonSurfaceNormal(polygon->getVertices().at(0).getCoordinates(), 
                                                                                            polygon->getVertices().at(1).getCoordinates(), 
                                                                                            polygon->getVertices().at(2).getCoordinates());
                            polygon->setSurfaceNormal(n);
                            polygon->hasVertexNormal = polygonalPatch;
                            scene.objects.push_back(polygon);
                        }else{
                            

                            vector<Vertex> verts;
                            int currentVertex = 0;
                            while(currentVertex < vertexCount){

                                getline(sceneFile, currentSceneLine);
                                if(currentSceneLine.front() != '#'){

                                    Vertex v;
                                    Eigen::Vector3d point;
                                    
                                    dataStream << currentSceneLine;

                                    dataStream >> point[0] >> point[1] >> point[2];
                                    if(polygonalPatch){
                                        Eigen::Vector3d vertexNormal;
                                        dataStream >> vertexNormal[0] >> vertexNormal[1] >> vertexNormal[2];
                                        v.setNormalVector(vertexNormal);
                                    }

                                    v.setCoordinates(point);
                                    verts.push_back(v);
                                    currentVertex++;

                                    clearStreamMacro(dataStream);
                                }
                            }

                            // used to ensure that fanning of polygons does not flip normal orientation of later polygons
                            Eigen::Vector3d n0 = Calculations::calculatePolygonSurfaceNormal(verts.at(0).getCoordinates(), 
                                                                                            verts.at(1).getCoordinates(), 
                                                                                            verts.at(2).getCoordinates());
                            Poly* priorPoly = nullptr;
                            Vertex seedVertex = verts.at(0);
                            Vertex v1, v2;
                            unsigned int i;
                            for (i = 1; i < verts.size() - 1; i++)
                            {
                                polygon = new Poly();
                                v1 = verts.at(i);
                                v2 = verts.at(i + 1);
                                polygon->appendVertex(seedVertex);
                                polygon->appendVertex(v1);
                                polygon->appendVertex(v2);
                                polygon->hasVertexNormal = polygonalPatch;
                                Eigen::Vector3d n = Calculations::calculatePolygonSurfaceNormal(polygon->getVertices().at(0).getCoordinates(), 
                                                                                                polygon->getVertices().at(1).getCoordinates(), 
                                                                                                polygon->getVertices().at(2).getCoordinates());
                                polygon->setSurfaceNormal(n);
                                polygon->setMaterial(currentMaterial);
                                // check if handling a concave polygon during fanning, and using comparisonPoly to correct orientation
                                if(priorPoly != nullptr){
                                    if(priorPoly->getSurfaceNormal().dot(polygon->getSurfaceNormal()) < 0){
                                        polygon->clearVertices();
                                        polygon->appendVertex(seedVertex);
                                        while(i < verts.size()){
                                            polygon->appendVertex(verts.at(i));
                                            i++;
                                        }
                                        polygon->setSurfaceNormal(n0.normalized());
                                        cout << "concave normal=" << polygon->getSurfaceNormal() << endl;
                                        scene.objects.push_back(polygon);
                                        priorPoly = nullptr;
                                        clearStreamMacro(dataStream);
                                        break;
                                    }
                                }
                                scene.objects.push_back(polygon);
                                priorPoly = polygon;
                            }
                            

                            
                        }

                        clearStreamMacro(dataStream);
                        id = "";
                        break;
                    }

                    default:
                        cout << "skipping..." << endl;
                        break;
                }
            }
            
            
            sceneFile.close();
        }else{
            throw new runtime_error("Unable to open scene file for processing");
        }

        
    }
    catch(const std::exception& e)
    {
        cout << e.what() << endl;
        // exit(-1);
    }
       
    return scene;
}












#endif
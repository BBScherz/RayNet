#ifndef _VERTEX_H
#define _VERTEX_H

#include <Eigen/Dense>

class Vertex{

    private:

        Eigen::Vector3d __coordinates;
        Eigen::Vector3d __normal;


    public:

        Vertex(){}

        Vertex(Eigen::Vector3d point, Eigen::Vector3d vertexNormal){
            this->__coordinates = point;
            this->__normal = vertexNormal;
        }

        ~Vertex(){}


        // vertex coordinates getter/setter
        void setCoordinates(Eigen::Vector3d point){
            this->__coordinates = point;
        }

        Eigen::Vector3d getCoordinates(){
            return this->__coordinates;
        }


        // vertex normal vector getter/setter
        void setNormalVector(Eigen::Vector3d normalVector){
            this->__normal = normalVector;
        }

        Eigen::Vector3d getNormalVector(){
            return this->__normal;
        }


};

#endif
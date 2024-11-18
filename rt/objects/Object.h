#ifndef _OBJECT_H
#define _OBJECT_H

#include <iostream>
#include <Eigen/Dense>
#include <vector>

#include "Vertex.h"
#include "../util/Calculations.h"
#include "../scene/Ray.h"
#include "../scene/Light.h"
#include "../scene/IntersectionRecord.h"
using namespace std;

struct Material
{
    double __red;
    double __green;
    double __blue;
    double __diffuseComponent;
    double __specularComponent;
    double __shine;
    double __transmittence;
    double __refractionIndex;

    friend ostream& operator << (ostream& out, const Material& m){
        return out << "\nMaterial Information:\n-------------\n"
        << "Red=" << m.__red << "\n"
        << "Green=" << m.__green << "\n"
        << "Blue=" << m.__blue << "\n"
        << "Diffuse=" << m.__diffuseComponent << "\n"
        << "Specular=" << m.__specularComponent << "\n"
        << "Shine=" << m.__shine << "\n"
        << "Transmittence=" << m.__transmittence << "\n"
        << "Refraction=" << m.__refractionIndex << endl;
    }
};


class Object{


    protected:
        struct Material __material;
        vector<Vertex> vertices;

    public:

        //this constant prevents objects reflecting off themselves
        const double __bias = 1e-6;

        virtual ~Object() = default;

        //all objects must be able to calculate if a ray has hit
        virtual bool calculateIntersection(IntersectionRecord& record, Ray r, double minimumDistance, double maximumDistance) = 0;
        virtual Eigen::Vector3d computeCompositeColor(IntersectionRecord& record, Ray r, vector<Light> lights, vector<Object*> objects, Eigen::Vector3d backdrop, int& recursionDepth, int maximumDepth) = 0;


        // bias getter
        double getBias(){
            return this->__bias;
        }


        // material setters/getters
        Material getMaterial(){
            return this->__material;
        }

        void setMaterial(Material m){

            this->__material.__red = m.__red;
            this->__material.__green = m.__green;
            this->__material.__blue = m.__blue;
            this->__material.__diffuseComponent = m.__diffuseComponent;
            this->__material.__specularComponent = m.__specularComponent;
            this->__material.__shine = m.__shine;
            this->__material.__transmittence = m.__transmittence;
            this->__material.__refractionIndex = m.__refractionIndex;

        }

};

#endif


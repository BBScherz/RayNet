#ifndef _POLY_H
#define _POLY_H
#include "Object.h"


class Poly : public Object{

    private:

        Eigen::Vector3d surfaceNormal;
        Eigen::Vector3d colorCalculationHelper(Light l, IntersectionRecord ir, Ray r, Material m, double lightIntensity);

    public:

        bool hasVertexNormal;

        Poly(){};
        Poly(Eigen::Vector3d position){};
        Poly(Eigen::Vector3d position, Eigen::Vector3d normal){};
        ~Poly(){}

        void appendVertex(stringstream& ss, bool hasVertexNormal);
        void appendVertex(Vertex v){
            this->vertices.push_back(v);
        }
        vector<Vertex> getVertices(){
            return this->vertices;
        }
        void clearVertices(){
            this->vertices.clear();
        }
        void setSurfaceNormal(Eigen::Vector3d n);
        Eigen::Vector3d getSurfaceNormal(){
            return this->surfaceNormal;
        }
        bool calculateIntersection(IntersectionRecord& record, Ray r, double minimumDistance, double maximumDistance);
        Eigen::Vector3d computeCompositeColor(IntersectionRecord& record, Ray r, vector<Light> lights, vector<Object*> objects, Eigen::Vector3d backdrop, int& recursionDepth, int maximumDepth);
};



void Poly::appendVertex(stringstream& ss, bool hasVertexNormal){

    Vertex v;
    Eigen::Vector3d coordinates;
    ss >> coordinates[0] >> coordinates[1] >> coordinates[2];
    if(hasVertexNormal){
        Eigen::Vector3d normalVector;
        ss >> normalVector[0] >> normalVector[1] >> normalVector[2];
        v.setNormalVector(normalVector);
    }
    v.setCoordinates(coordinates);

    this->vertices.push_back(v);

}

void Poly::setSurfaceNormal(Eigen::Vector3d n){
    this->surfaceNormal = n;
}


bool Poly::calculateIntersection(IntersectionRecord& record, Ray r, double minimumDistance, double maximumDistance) {

    if(this->vertices.size() == 3){

        Eigen::Matrix3d lhs;
        lhs << (this->vertices[1].getCoordinates() - this->vertices[0].getCoordinates()), (this->vertices[2].getCoordinates() - this->vertices[0].getCoordinates()), -1 * r.getDirection();
     
        Eigen::Vector3d rhs(r.getOrigin() - this->vertices[0].getCoordinates());
        Eigen::Vector3d product = lhs.inverse() * rhs;

        bool a = product[0] >= 0 && product[1] >= 0;
        bool b = (product[0] + product[1]) <= 1;
        bool c = product[2] <= maximumDistance && product[2] >= minimumDistance;

        if(a && b && c){

            record.setIntersectionDistance(product[2]);
            record.setIntersectionPoint(r.getOrigin() + (r.getDirection() * product[2]));
            if(this->hasVertexNormal){
                Eigen::Vector3d n = vertices.at(0).getNormalVector() + (product[0] * (vertices.at(1).getNormalVector() - vertices.at(0).getNormalVector())) + (product[1] * (vertices.at(2).getNormalVector() - vertices.at(0).getNormalVector()));
                record.setIntersectionNormal(n);
            }else{
                record.setIntersectionNormal(this->surfaceNormal);
            }

            return true;
        }
    }else{
        
        int projectionCoordinateOne;
        int projectionCoordinateTwo;
        double distanceToInterseciton = ((vertices.at(0).getCoordinates() - r.getOrigin()).dot(surfaceNormal)) / r.getDirection().dot(surfaceNormal);
        if(distanceToInterseciton > maximumDistance){return false;}
        Eigen::Vector3d polygonIntersectionCoordinates = r.getOrigin() + (r.getDirection() * distanceToInterseciton);

        double absoluteNormalX = abs(surfaceNormal[0]);
        double absoluteNormalY = abs(surfaceNormal[1]);
        double absoluteNormalZ = abs(surfaceNormal[2]);

        if((absoluteNormalZ > absoluteNormalX) && (absoluteNormalZ > absoluteNormalX)){
            projectionCoordinateOne = 0;
            projectionCoordinateTwo = 1;
        }else if((absoluteNormalY > absoluteNormalX)){
            projectionCoordinateOne = 0;
            projectionCoordinateTwo = 2;
        }else{
            projectionCoordinateOne = 1;
            projectionCoordinateTwo = 2;
        }

        double s;
        double a;
        int edgeIntersections = 0;
        Eigen::Vector2d planarProjectedIntersection = {polygonIntersectionCoordinates[projectionCoordinateOne], polygonIntersectionCoordinates[projectionCoordinateTwo]};
        
        for(unsigned int v = 0; v < vertices.size() - 1; v++){

            Eigen::Matrix2d l;
            Eigen::Vector2d j(1, 0);

            Eigen::Vector2d v0(vertices.at(v).getCoordinates()[projectionCoordinateOne], vertices.at(v).getCoordinates()[projectionCoordinateTwo]);
            Eigen::Vector2d v1(vertices.at(v + 1).getCoordinates()[projectionCoordinateOne], vertices.at(v + 1).getCoordinates()[projectionCoordinateTwo]);

            Eigen::Vector2d r(v0 - planarProjectedIntersection);

            l.col(0) = v0 - v1;
            l.col(1) = j;

            a = (l.inverse() * r)[0];
            if(a <= 1 && a >= 0){

                s = (l.inverse() * r)[1];
                if(s >= 0){
                    edgeIntersections++;
                }
            }

        }

        Eigen::Matrix2d l;
        Eigen::Vector2d j(1, 0);
        Eigen::Vector2d v0(vertices.at(0).getCoordinates()[projectionCoordinateOne], vertices.at(0).getCoordinates()[projectionCoordinateTwo]);
        Eigen::Vector2d v1(vertices.at(vertices.size() - 1).getCoordinates()[projectionCoordinateOne], vertices.at(vertices.size() - 1).getCoordinates()[projectionCoordinateTwo]);
        Eigen::Vector2d r0(v1 - planarProjectedIntersection);
        l.col(0) = v1 - v0;
        l.col(1) = j;
        a = (l.inverse() * r0)[0];
        if(a <= 1 && a >= 0){
            s = (l.inverse() * r0)[1];
            if(s >= 0){
                edgeIntersections++;
            }
        }

        
        if(edgeIntersections % 2 == 1){
            record.setIntersectionDistance(distanceToInterseciton);
            record.setIntersectionPoint(r.getOrigin() + (r.getDirection() * distanceToInterseciton));
            record.setIntersectionNormal(surfaceNormal);
            return true;
        }
    }

    return false;
}

Eigen::Vector3d Poly::computeCompositeColor(IntersectionRecord& record, Ray r, vector<Light> lights, vector<Object*> objects, Eigen::Vector3d backdrop, int& recursionDepth, int maximumDepth){

    Eigen::Vector3d compositeColor;
    compositeColor.setZero();
    double lightIntensity = 1.0 / sqrt(lights.size());

    for(Light l: lights){

        bool isPointInShadow = false;
        IntersectionRecord shadowCastRecord;
        Eigen::Vector3d lightDirection = (l.xyz - record.getIntersectionPoint()).normalized();
        double distanceToLight = (l.xyz - record.getIntersectionPoint()).dot(lightDirection) / lightDirection.dot(lightDirection);
        Ray shadowCastRay(record.getIntersectionPoint(), lightDirection);
        for(Object* ob: objects){
            if(ob->calculateIntersection(shadowCastRecord, shadowCastRay, __bias, INFINITY)){
                if(shadowCastRecord.getIntersectionDistance() >= __bias && shadowCastRecord.getIntersectionDistance() <= distanceToLight){
                    isPointInShadow = true;
                    break;
                }
                
            }
        }

        if(!isPointInShadow){
            Eigen::Vector3d color = colorCalculationHelper(l, record, r, this->getMaterial(), lightIntensity);
            compositeColor[0] += color[0];
            compositeColor[1] += color[1];
            compositeColor[2] += color[2];
        } 
    }

    double directionNormalProduct = r.getDirection().normalized().dot(record.getIntersectionNormal().normalized());
    Eigen::Vector3d reflectionDirection = r.getDirection().normalized() - (2 * directionNormalProduct * record.getIntersectionNormal().normalized());
    IntersectionRecord reflectionIntersectionRecord;
    Ray reflectionRay(record.getIntersectionPoint(), reflectionDirection);

    double maximumReflectionDistance = INFINITY;
    Object* nearestObject = nullptr;
    for(Object* nextObject: objects){
        if(nextObject->calculateIntersection(reflectionIntersectionRecord, reflectionRay, __bias, maximumReflectionDistance)){
            if(reflectionIntersectionRecord.getIntersectionDistance() < maximumReflectionDistance){
                nearestObject = nextObject;
                maximumReflectionDistance = reflectionIntersectionRecord.getIntersectionDistance();
            }
        }
    }

    if(maximumReflectionDistance == INFINITY){
        return compositeColor += this->getMaterial().__specularComponent * backdrop;
    }
    
    if(recursionDepth + 1 < maximumDepth && this->getMaterial().__specularComponent > 0.0){
        recursionDepth++;
        reflectionRay.setOrigin(reflectionIntersectionRecord.getIntersectionPoint());
        reflectionRay.setDirection((-1 * reflectionDirection.normalized()) + (2 * reflectionDirection.normalized().dot(reflectionIntersectionRecord.getIntersectionNormal().normalized()) * reflectionIntersectionRecord.getIntersectionNormal().normalized()));
        compositeColor += this->getMaterial().__specularComponent * nearestObject->computeCompositeColor(reflectionIntersectionRecord, reflectionRay, lights, objects, backdrop, recursionDepth, maximumDepth);
    }

    return compositeColor;
}


Eigen::Vector3d Poly::colorCalculationHelper(Light l, IntersectionRecord ir, Ray r, Material m, double lightIntensity){
    
    Eigen::Vector3d intersectedNormal = ir.getIntersectionNormal().normalized();
    Eigen::Vector3d pointToLightDirection = (l.xyz - ir.getIntersectionPoint()).normalized();
    Eigen::Vector3d inverseRayDirection = (-1 * r.getDirection()).normalized();
    Eigen::Vector3d halfwayVector = (pointToLightDirection + inverseRayDirection).normalized();

    double colorDiffusion = max(0.0, intersectedNormal.dot(pointToLightDirection));
    double specularHighlight = pow(max(0.0, intersectedNormal.dot(halfwayVector)), m.__shine);

    double red = ((m.__red * colorDiffusion * m.__diffuseComponent) + (specularHighlight * m.__specularComponent)) * (lightIntensity * l.rgb[0]);
    double green = ((m.__green * colorDiffusion * m.__diffuseComponent) + (specularHighlight * m.__specularComponent)) * (lightIntensity * l.rgb[1]);
    double blue = ((m.__blue * colorDiffusion * m.__diffuseComponent) + (specularHighlight * m.__specularComponent)) * (lightIntensity * l.rgb[2]);
    
    Eigen::Vector3d composite(red, green, blue);
    return composite;
}

#endif
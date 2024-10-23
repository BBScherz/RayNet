#ifndef _INTERSECTION_RECORD_H
#define _INTERSECTION_RECORD_H
#include <Eigen/Dense>

class IntersectionRecord{

    private:
        double __rayDistance;
        Eigen::Vector3d __intersectionPoint;
        Eigen::Vector3d __intersectionRGB;
        Eigen::Vector3d __intersectionNormal;

    public:
        IntersectionRecord(){}
        void setIntersectionDistance(double t){
            this->__rayDistance = t;
        }
        void setIntersectionPoint(Eigen::Vector3d p){
            this->__intersectionPoint = p;
        }
        void setIntersectionRGB(Eigen::Vector3d rgb){
            this->__intersectionRGB = rgb;
        }
        void setIntersectionNormal(Eigen::Vector3d n){
            this->__intersectionNormal = n;
        }

        double getIntersectionDistance(){
            return this->__rayDistance;
        }
        Eigen::Vector3d getIntersectionPoint(){
            return this->__intersectionPoint;
        }
        Eigen::Vector3d getIntersectionRGB(){
            return this->__intersectionRGB;
        }
        Eigen::Vector3d getIntersectionNormal(){
            return this->__intersectionNormal;
        }
};
#endif
#ifndef _RAY_H
#define _RAY_H

#include <Eigen/Dense>

class Ray{

    private:
        Eigen::Vector3d __origin;
        Eigen::Vector3d __direction;

    public:
        Ray(Eigen::Vector3d origin, Eigen::Vector3d direction){
            this->__origin = origin;
            this->__direction = direction;
        }

        void setOrigin(Eigen::Vector3d o){
            this->__origin = o;
        }

        void setDirection(Eigen::Vector3d d){
            this->__direction = d;
        }

        Eigen::Vector3d getOrigin(){
            return this->__origin;
        }
        
        Eigen::Vector3d getDirection(){
            return this->__direction;
        }
};

#endif
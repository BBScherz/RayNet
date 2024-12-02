#ifndef _CAMERA_H
#define _CAMERA_H

#include <iostream>
#include <vector>
#include <Eigen/Dense>

class Camera{

    private:
        Eigen::Vector3d __w;
        Eigen::Vector3d __u;
        Eigen::Vector3d __v;

    public:
        Camera(){}
        Camera(Eigen::Vector3d from, Eigen::Vector3d at, Eigen::Vector3d up);

        Eigen::Vector3d getW();
        Eigen::Vector3d getU();
        Eigen::Vector3d getV();

};


Camera::Camera(Eigen::Vector3d from, Eigen::Vector3d at, Eigen::Vector3d up){
    this->__w = -1 * (at - from).normalized();
    this->__u = up.cross(this->__w).normalized();
    this->__v = this->__w.cross(this->__u).normalized();
}

Eigen::Vector3d Camera::getW(){
    return this->__w;
}

Eigen::Vector3d Camera::getU(){
    return this->__u;
}

Eigen::Vector3d Camera::getV(){
    return this->__v;
}

#endif
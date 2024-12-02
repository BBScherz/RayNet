
#ifndef _LIGHT_H
#define _LIGHT_H
#include <Eigen/Dense>
using namespace std;

class Light{

    private:
        

    public:
        Light(){}
        Eigen::Vector3d xyz;
        Eigen::Vector3d rgb;
};
#endif

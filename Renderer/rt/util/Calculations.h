#include <iostream>
#include <Eigen/Dense>
#include <sstream>
#include <random>
#include "../scene/Camera.h"

#define PI 3.1415926535

class Calculations{

    private:
        // static std::random_device secureRandom;

    public:

        //Macro for surface normal calculation of a polygon
        static Eigen::Vector3d calculatePolygonSurfaceNormal(Eigen::Vector3d a, Eigen::Vector3d b, Eigen::Vector3d c){
            Eigen::Vector3d mp1 = b - a;
            Eigen::Vector3d mp2 = c - a;
            return mp1.cross(mp2).normalized();
        }

        static double degreesToRadians(double fov){
            return fov * (PI / 180.0);
        }

        static double sceneBorderWidth(double theta){
            return tan(degreesToRadians(theta / 2.0));
        }

        static double calculatePixelWidth(double sceneWidth, int horizontalResolution){
            return (sceneWidth * 2) / (double)horizontalResolution;
        }

        static Eigen::Vector3d calculatePixelCenterCoordinates(int horizontalResolution, int verticalResolution, int pixelXCoordinate, int pixelYCoordinate, double pixelWidth, double theta, double distance){
            
            std::random_device secureRandom;
            std::mt19937 gen(secureRandom());
            std::uniform_real_distribution dist(-(3.0 * pixelWidth)/8.0, (3.0 * pixelWidth)/8.0);

            double xJitter = dist(gen);
            double yJitter = dist(gen);

            double sceneAspectRatio = (double)horizontalResolution / (double)verticalResolution;
            Eigen::Vector3d pixelCenterCoordinate;
            pixelCenterCoordinate[0] = (-1 * distance) * theta + (pixelWidth / 2.0) + (pixelWidth * pixelXCoordinate);
            pixelCenterCoordinate[1] = distance * (theta / sceneAspectRatio) - (pixelWidth / 2.0) - (pixelWidth * pixelYCoordinate);
            pixelCenterCoordinate[2] = -1 * distance;

            pixelCenterCoordinate[0] += xJitter;
            pixelCenterCoordinate[1] += yJitter;

            return pixelCenterCoordinate;
        }

        static Eigen::Vector3d pixelCoordinatesToWorldCoordinates(Eigen::Vector3d pixelCoordinates, Camera* camera){
            Eigen::Vector3d convertedX = pixelCoordinates[0] * camera->getU();
            Eigen::Vector3d convertedY = pixelCoordinates[1] * camera->getV();
            Eigen::Vector3d convertedZ = pixelCoordinates[2] * camera->getW();

            return convertedX + convertedY + convertedZ;
        }

        
};
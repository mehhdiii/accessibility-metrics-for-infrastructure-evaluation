#pragma once
#include <vector>
#include <string>
// #include <pcl/io/pcd_io.h>
// #include <pcl/point_types.h>

void saveStairsToDatabase(
    const std::string& host,
    unsigned int port,
    const std::string& user,
    const std::string& password,
    const std::string& dbName,
    float step_depth,
    float step_height,
    float step_width,
    float slope_deg,
    float stair_angle_deg,
    int stairParts,
    float distX,
    float distY,
    float distPar,
    float distOrt,
    float anchorPoint,
    int risers,
    int treads,
    int point_cloud_id
);

pcl::PointCloud<pcl::PointXYZ>::Ptr loadPointCloudFromMySQL(
    const std::string& host,
    unsigned int port,
    const std::string& user,
    const std::string& password,
    const std::string& dbName,
    int id
);
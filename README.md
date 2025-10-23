# accessibility-metrics-for-infrastructure-evaluation

# TurtleBot4 + Ignition + PCL Pipeline

This guide describes how to run a TurtleBot4 simulation in Ignition Gazebo, bridge ROS 2 topics, collect point cloud data, and run point cloud processing algorithms.

use the compose file to create relevant containers for:
1. ros2
2. database (mysql)
3. stairway detection algorithm (https://github.com/ThomasWestfechtel/StairwayDetection)

use the following compose command on repository root:
```bash
docker compose up -d
```
---

## 1. Access the ROS 2 Container

```bash
docker container exec -it ros-humble-container bash
```

---

## 2. Start the TurtleBot4 World in Ignition

```bash
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py
```

---

## 3. Map Gazebo Topics to ROS 2

Run the ROS–Ignition bridge to map camera and point cloud topics:

```bash
ros2 run ros_gz_bridge parameter_bridge \
/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/image@sensor_msgs/msg/Image[ignition.msgs.Image \
/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image \
/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked \
/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo
```

---

## 4. (Optional) Start RViz2 for Visualization

```bash
rviz2 rviz2
```

---

## 5. Capture a Point Cloud Frame and Save It to the Database

Drive the robot to the desired position, then save the captured point cloud to the database:

```bash
python3 point-cloud-db-writer.py <pt_name> <pt_frame_number>
```

**Example:**
```bash
python3 point-cloud-db-writer.py stair_entry 12
```

---

## 6. Access the PCL Development Container

```bash
docker container exec -it pcl-dev-container bash
```

---

## 7. Run the Point Cloud Processing Algorithm

Run the algorithm with the specified point cloud ID and database parameters.  
Use the `--enable-viewer` flag to visualize the processed point cloud.

```bash
./stair_det <point_cloud_id> ../point-clouds/output.pcd mysql 3306 stairuser stairpass stairs_db --enable-viewer
```

**Example:**
```bash
./stair_det 42 ../point-clouds/output.pcd mysql 3306 stairuser stairpass stairs_db --enable-viewer
```

---

## Notes

- Ensure both containers (`ros-humble-container` and `pcl-dev-container`) are running and networked properly.  
- The database credentials and connection parameters can be configured in your environment or passed as arguments.  
- The script `point-cloud-db-writer.py` creates point cloud entries in the database.  
- The executable `stair_det` performs point cloud processing and optionally visualizes the result using PCL’s viewer.

---

**Author:**  
*Generated for the TurtleBot4 + Ignition + PCL simulation pipeline.*

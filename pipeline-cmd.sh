

#in the following container:
docker container exec -it ros-humble-container bash

##### EITHER:

#run this launch file to spin up everything:
ros2 launch every_launch_ever pipeline.py

##### OR 

#start the world with turtlebot
ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py

# map gz topics to ros2:
ros2 run ros_gz_bridge parameter_bridge /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/image@sensor_msgs/msg/Image[ignition.msgs.Image /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo

#start rviz (optional):
#fixed frame: oakd_rgb_camera_optical_frame
#tc topic: /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points 

#run service to read metrics:
ros2 run db_reader get_stair_case_metrics_service

#run service to write pointcloud to db:
ros2 run pc_saver pc_saver_service

#run orchestrator:
ros2 run orchestrator staircase_orchestration_service

rviz2 rviz2

#ros2 topic list










##OBSOLETE STEPS
# # drive robot to relevant position and create pointcloud frame entry in db:
# python3 point-cloud-db-writer.py <pt_name> <pt_frame_number>

# #Now connect pcl container:
# docker container exec -it pcl-dev-container bash

# #run the algorithm script (specify point_cloud_id and db params as args). use --enable-viewer if you want to view the algorithms output point cloud
# ./stair_det <point_cloud_id> ../point-clouds/output.pcd mysql 3306 stairuser stairpass stairs_db --enable-viewer


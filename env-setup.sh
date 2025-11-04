apt update && 
apt install ros-humble-xacro && 
apt install ros-humble-joint-state-publisher && 
apt install ros-humble-gazebo-ros2-control &&
apt install ros-humble-plansys2-domain-expert && 
apt install ros-humble-gtest-vendor && 
apt install ros-humble-rqt-gui-cpp && 
apt install ros-humble-rclcpp-cascade-lifecycle && 
apt install ros-humble-behaviortree-cpp-v3 && 
apt install ros-humble-test-msgs && 
apt install libreadline-dev && 
apt install ros-humble-nav2-msgs && 
apt install ros-humble-navigation2 -y && 
apt install ros-humble-nav2-bringup && 
apt install ros-humble-ros2-control && 
apt install ros-humble-ros2-controllers &&
apt install ros-humble-behaviortree-cpp && 
apt install ros-humble-plansys2-pddl-parser &&
apt install libsuitesparse-dev &&
apt install ros-humble-rviz2 && 
apt install ros-humble-gazebo-ros-pkgs &&
apt install '~nros-humble-rqt*' &&
# cp -r /data/data/aruco_ros/aruco_ros/models /root/.gazebo/models &&
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
# echo 'source /data/ros_ws/install/setup.bash' >> ~/.bashrc


#install gazebo ignition:
echo 'export IGN_GAZEBO_RESOURCE_PATH=$IGN_GAZEBO_RESOURCE_PATH:/usr/share/gazebo-11/models' >> ~/.bashrc
sudo apt-get update
sudo apt-get install lsb-release gnupg
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install ignition-fortress

sudo apt install ros-humble-robot-localization



#install pip
sudo apt update
sudo apt install python3-pip

#install zsh
sudo apt update
sudo apt install nano
sudo apt install zsh-autosuggestions zsh-syntax-highlighting zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"


#aliases
alias ss="source /data/ros_ws/install/setup.bash"

#launch commands:
#ros2 launch turtlebot4_ignition_bringup turtlebot4_ignition.launch.py

# ros2 run ros_gz_bridge parameter_bridge \
# /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/image@sensor_msgs/msg/Image[ignition.msgs.Image \
# /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image \
# /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked \
# /world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo

#rviz2 rviz2

#to check the frame transformations:
#ros2 topic echo /tf_static | grep oakd

pip3 install open3d
pip3 install numpy
sudo apt install ros-humble-rqt-graph

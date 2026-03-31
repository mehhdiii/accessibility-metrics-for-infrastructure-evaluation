FROM ros:humble

SHELL ["/bin/bash", "-c"]

# --------------------
# System dependencies
# --------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    git cmake build-essential curl wget lsb-release gnupg2 \
    python3-pip python3-colcon-common-extensions \
    python3-numpy python3-opencv python3-mysql.connector \
    libmysqlclient-dev libssl-dev \
    libogre1.12.1 \
    ros-humble-rviz2 \
    ros-humble-cv-bridge ros-humble-vision-opencv \
 && rm -rf /var/lib/apt/lists/*

# --------------------
# Python deps
# --------------------
RUN pip install --upgrade pip && \
    pip install "numpy<2" mysql-connector-python open3d requests

# # --------------------
# # Gazebo (Ignition) + bridge
# # --------------------
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ros-humble-ros-gz-bridge ros-humble-ros-gz-sim \
#  && rm -rf /var/lib/apt/lists/*

## install new gazebo fortress: 

RUN apt-get update && apt-get install -y wget
RUN sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
RUN wget http://packages.osrfoundation.org/gazebo.key -O - | apt-key add -
RUN apt-get update && apt-get install -y ignition-fortress


# Install ROS2 RealSense package
RUN apt-get update && apt-get install -y \
    ros-humble-realsense2-camera \
    && rm -rf /var/lib/apt/lists/*


 # Install CycloneDDS RMW
RUN apt-get update && apt-get install -y ros-humble-rmw-cyclonedds-cpp
# Set CycloneDDS as default DDS
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

# Auto-source workspace on container start
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source /data/ros_ws/install/setup.bash" >> ~/.bashrc

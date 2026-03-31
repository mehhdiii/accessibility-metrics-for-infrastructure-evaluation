from launch import LaunchDescription
from launch_ros.actions import Node

from dotenv import load_dotenv
import os, yaml

#specify name of the node for reading config
node_name = "pointcloud_maker"

#load config:
load_dotenv()
config_path = os.getenv("ROS_TOPICS_FILE", "/data/ros_ws/src/common_configs/topics.yaml")
with open(config_path) as f:
    config = yaml.safe_load(f)

#fetch relevant node's config
node_configs = config[node_name]

print(node_configs)

image_raw = node_configs["topics"]["image"]
depth_image = node_configs["topics"]["depth_image"]
camera_info = node_configs["topics"]["camera_info"]
point_cloud_topic = node_configs["topics"]["point_cloud"]

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='depth_image_proc',
            executable='point_cloud_xyzrgb_node',
            name='pointcloud_from_depth',
            remappings=[
                ('rgb/image_rect_color', image_raw),
                ('depth_registered/image_rect', depth_image),
                ('rgb/camera_info', camera_info),
                ('points', point_cloud_topic),
            ],
            parameters=[{
                'publisher_qos': 'RELIABLE'
            }],
            output='screen'
        )
    ])

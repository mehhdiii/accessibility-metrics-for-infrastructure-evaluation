# launch/all_nodes_launch.py
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

from dotenv import load_dotenv
import os, yaml

# #specify name of the node for reading config
node_name = "pipeline"

# #load config:
load_dotenv()
config_path = os.getenv("ROS_TOPICS_FILE", "/data/ros_ws/src/common_configs/topics.yaml")
with open(config_path) as f:
    config = yaml.safe_load(f)

# #fetch relevant node's config
env_configs = config["env"]

node_configs = config[node_name]


def generate_launch_description():

    launch_actions = [
        # 3. Start db_reader service
        Node(
            package='db_reader',
            executable='get_stair_case_metrics_service',
            name='db_reader_service',
            output='screen'
        ),

        # 4. Start pc_saver service
        Node(
            package='pc_saver',
            executable='pc_saver_service',
            name='pc_saver_service',
            output='screen'
        ),

        # 5. Start orchestrator service
        Node(
            package='orchestrator',
            executable='staircase_orchestration_service',
            name='staircase_orchestration_service',
            output='screen'
        ),

        # 6. Start RViz2
        ExecuteProcess(
            cmd=['rviz2'],
            output='screen'
        ),
    ]

    if (env_configs["simulation"]):
            # 1. Start TurtleBot world

            launch_actions.append(ExecuteProcess(
                cmd=['ros2', 'launch', 'turtlebot4_ignition_bringup', 'turtlebot4_ignition.launch.py'],
                output='screen'
            ))

            # 2. Start ros_gz_bridge for the RGB-D camera
            launch_actions.append(
                ExecuteProcess(
                    cmd=[
                        'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
                        f'{node_configs["topics"]["image"]}@{node_configs["topics"]["gz_image"]}',
                        f'{node_configs["topics"]["depth_image"]}@{node_configs["topics"]["gz_depth_image"]}',
                        f'{node_configs["topics"]["pointcloud"]}@{node_configs["topics"]["gz_pointcloud"]}',
                        f'{node_configs["topics"]["image_info"]}@{node_configs["topics"]["gz_image_info"]}'
                    ],
                    output='screen'
                )
            )


    return LaunchDescription(launch_actions)

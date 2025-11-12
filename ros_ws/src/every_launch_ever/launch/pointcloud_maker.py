from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='depth_image_proc',
            executable='point_cloud_xyzrgb_node',
            name='pointcloud_from_depth',
            remappings=[
                ('rgb/image_rect_color', '/camera/camera/color/image_raw'),
                ('depth_registered/image_rect', '/camera/camera/aligned_depth_to_color/image_raw'),
                ('rgb/camera_info', '/camera/camera/color/camera_info'),
                ('points', '/manuallycomputed/points'),
            ],
            parameters=[{
                'publisher_qos': 'RELIABLE'
            }],
            output='screen'
        )
    ])

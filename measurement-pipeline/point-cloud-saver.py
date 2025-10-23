import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import open3d as o3d
import sensor_msgs_py.point_cloud2 as pc2
import numpy as np

class PCSaver(Node):
    def __init__(self):
        super().__init__('pc_saver')
        self.sub = self.create_subscription(
            PointCloud2,
            '/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points',
            self.pc_callback,
            10
        )

    def pc_callback(self, msg):
        # Read points as a generator and convert to Nx3 float array
        points_list = []
        for p in pc2.read_points(msg, field_names=("x","y","z"), skip_nans=True):
            points_list.append([float(p[0]), float(p[1]), float(p[2])])
        
        if not points_list:
            self.get_logger().warn("No points found in point cloud")
            return

        points_array = np.array(points_list, dtype=np.float32)
        pc = o3d.geometry.PointCloud()
        pc.points = o3d.utility.Vector3dVector(points_array)
        o3d.io.write_point_cloud("point-clouds/frame.pcd", pc)
        self.get_logger().info("Saved point cloud as frame.pcd")
        rclpy.shutdown()

rclpy.init()
node = PCSaver()
rclpy.spin(node)

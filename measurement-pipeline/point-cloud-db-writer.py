import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import open3d as o3d
import numpy as np
import io
import mysql.connector
from datetime import datetime
import sys
import tempfile

# --- MySQL config ---
MYSQL_HOST = "mysql"          # Docker container host
MYSQL_USER = "stairuser"
MYSQL_PASSWORD = "stairpass"
MYSQL_DB = "stairs_db"
MYSQL_PORT = 3306

class PCSaver(Node):
    def __init__(self, pc_name: str, frame_number: int = 0):
        super().__init__('pc_saver')
        self.pc_name = pc_name
        self.frame_number = frame_number

        self.sub = self.create_subscription(
            PointCloud2,
            '/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points',
            self.pc_callback,
            10
        )

    def pc_callback(self, msg):
        # Convert ROS PointCloud2 to Nx3 numpy array
        points_list = []
        for p in pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True):
            points_list.append([float(p[0]), float(p[1]), float(p[2])])

        if not points_list:
            self.get_logger().warn("No points found in point cloud")
            return

        points_array = np.array(points_list, dtype=np.float32)

        # Create Open3D point cloud
        pc = o3d.geometry.PointCloud()
        pc.points = o3d.utility.Vector3dVector(points_array)

        with tempfile.NamedTemporaryFile(suffix=".pcd") as tmpfile:
            o3d.io.write_point_cloud(tmpfile.name, pc)
            tmpfile.seek(0)
            pcd_bytes = tmpfile.read()
            # # Serialize point cloud to memory buffer (PCD)
            # pcd_bytes = o3d.io.write_point_cloud_to_bytes(
            #     pc,
            #     "pcd",          # format
            #     write_ascii=False,
            #     compressed=False,
            #     print_progress=False
            # )

            # Insert into MySQL
            try:
                conn = mysql.connector.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    port=MYSQL_PORT
                )
                cursor = conn.cursor()
                sql = """
                    INSERT INTO pointclouds (name, frame_number, data)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (self.pc_name, self.frame_number, pcd_bytes))
                conn.commit()
                self.get_logger().info(f"Saved point cloud '{self.pc_name}' to MySQL, ID: {cursor.lastrowid}")
            except mysql.connector.Error as e:
                self.get_logger().error(f"MySQL error: {e}")
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

        rclpy.shutdown()


if __name__ == "__main__":
    rclpy.init()

    if len(sys.argv) < 2:
        print("Usage: python pc_saver.py <pointcloud_name> [frame_number]")
        sys.exit(1)

    name = sys.argv[1]
    frame_num = int(sys.argv[2]) if len(sys.argv) >= 3 else 0

    node = PCSaver(name, frame_num)
    rclpy.spin(node)

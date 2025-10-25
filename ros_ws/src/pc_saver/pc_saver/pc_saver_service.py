import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
import open3d as o3d
import numpy as np
import mysql.connector
import tempfile
from every_interface_ever.srv import SavePointCloud

# --- MySQL config ---
MYSQL_HOST = "mysql"
MYSQL_USER = "stairuser"
MYSQL_PASSWORD = "stairpass"
MYSQL_DB = "stairs_db"
MYSQL_PORT = 3306


class PCSaverService(Node):
    def __init__(self):
        super().__init__('pc_saver_service')

        # Subscribe to point cloud topic
        self.subscription = self.create_subscription(
            PointCloud2,
            '/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points',
            self.pc_callback,
            10
        )

        # Service definition
        self.srv = self.create_service(SavePointCloud, 'save_pointcloud', self.save_pointcloud_callback)

        self.latest_msg = None
        self.get_logger().info("PCSaverService ready. Waiting for /save_pointcloud requests...")

    def pc_callback(self, msg):
        """Store the latest received PointCloud2 message."""
        self.latest_msg = msg

    def save_pointcloud_callback(self, request, response):
        """Triggered when /save_pointcloud service is called."""
        if self.latest_msg is None:
            response.success = False
            response.message = "No point cloud data received yet."
            self.get_logger().warn(response.message)
            return response

        try:
            # Convert PointCloud2 to Nx3 numpy array
            points = [
                [float(p[0]), float(p[1]), float(p[2])]
                for p in pc2.read_points(self.latest_msg, field_names=("x", "y", "z"), skip_nans=True)
            ]

            if not points:
                response.success = False
                response.message = "Point cloud is empty."
                self.get_logger().warn(response.message)
                return response

            points_array = np.array(points, dtype=np.float32)
            pc = o3d.geometry.PointCloud()
            pc.points = o3d.utility.Vector3dVector(points_array)

            with tempfile.NamedTemporaryFile(suffix=".pcd") as tmpfile:
                o3d.io.write_point_cloud(tmpfile.name, pc)
                tmpfile.seek(0)
                pcd_bytes = tmpfile.read()

                # Insert into MySQL
                conn = mysql.connector.connect(
                    host=MYSQL_HOST,
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    database=MYSQL_DB,
                    port=MYSQL_PORT
                )
                cursor = conn.cursor()
                sql = "INSERT INTO pointclouds (name, frame_number, data) VALUES (%s, %s, %s)"
                cursor.execute(sql, (request.name, request.frame_number, pcd_bytes))
                conn.commit()
                record_id = cursor.lastrowid

                response.success = True
                response.message = f"Saved point cloud '{request.name}' (ID: {record_id})"
                response.pointcloud_id = record_id
                self.get_logger().info(response.message)

        except mysql.connector.Error as e:
            response.success = False
            response.message = f"MySQL error: {e}"
            self.get_logger().error(response.message)

        except Exception as e:
            response.success = False
            response.message = f"Error: {e}"
            self.get_logger().error(response.message)

        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        return response


def main(args=None):
    rclpy.init(args=args)
    node = PCSaverService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

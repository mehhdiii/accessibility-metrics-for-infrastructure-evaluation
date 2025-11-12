import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, Image, CameraInfo
import sensor_msgs_py.point_cloud2 as pc2
import open3d as o3d
import numpy as np
import mysql.connector
import tempfile
import cv2
from cv_bridge import CvBridge
import json
from every_interface_ever.srv import SavePointCloud

# --- MySQL config ---
MYSQL_HOST = "localhost"
MYSQL_USER = "stairuser"
MYSQL_PASSWORD = "stairpass"
MYSQL_DB = "stairs_db"
MYSQL_PORT = 3306


class PCSaverService(Node):
    def __init__(self):
        super().__init__('pc_saver_service')

        self.latest_pc = None
        self.latest_image = None
        self.latest_camera_info = None
        self.bridge = CvBridge()

        # Subscribe to point cloud
        self.create_subscription(
            PointCloud2,
            # '/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/points',
            '/camera/camera/depth/color/points',
            self.pc_callback,
            10
        )

        # Subscribe to RGB image
        self.create_subscription(
            Image,
            # '/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/image',
            '/camera/camera/color/image_raw',
            self.image_callback,
            10
        )

        # Subscribe to camera info
        self.create_subscription(
            CameraInfo,
            # '/world/default/model/turtlebot4/link/oakd_rgb_camera_frame/sensor/rgbd_camera/camera_info',
            '/camera/camera/depth/camera_info',
            self.camera_info_callback,
            10
        )

        # Service
        self.srv = self.create_service(SavePointCloud, 'save_pointcloud', self.save_pointcloud_callback)

        self.get_logger().info("PCSaverService ready. Waiting for /save_pointcloud requests...")

    def pc_callback(self, msg):
        self.latest_pc = msg

    def image_callback(self, msg):
        self.latest_image = msg

    def camera_info_callback(self, msg):
        self.latest_camera_info = msg

    def save_pointcloud_callback(self, request, response):
        if self.latest_pc is None:
            response.success = False
            response.message = "No point cloud received yet."
            self.get_logger().warn(response.message)
            return response
        if self.latest_image is None:
            response.success = False
            response.message = "No image received yet."
            self.get_logger().warn(response.message)
            return response
        if self.latest_camera_info is None:
            response.success = False
            response.message = "No camera info received yet."
            self.get_logger().warn(response.message)
            return response

        try:
            # --- Point Cloud ---
            points = [
                [float(p[0]), float(p[1]), float(p[2])]
                for p in pc2.read_points(self.latest_pc, field_names=("x", "y", "z"), skip_nans=True)
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

            # --- Image ---
            cv_image = self.bridge.imgmsg_to_cv2(self.latest_image, desired_encoding='rgb8')
            _, img_buffer = cv2.imencode('.png', cv_image)
            img_bytes = img_buffer.tobytes()

            # --- Camera Params ---
            cam_info = self.latest_camera_info
            camera_params = {
                "fx": cam_info.k[0],
                "fy": cam_info.k[4],
                "cx": cam_info.k[2],
                "cy": cam_info.k[5],
                "distortion": list(cam_info.d),
                "frame_id": cam_info.header.frame_id,
                "width": cam_info.width,
                "height": cam_info.height
            }
            camera_params_json = json.dumps(camera_params)

            # --- Insert into MySQL ---
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=MYSQL_PORT
            )
            cursor = conn.cursor()
            sql = """
                INSERT INTO pointclouds (name, frame_number, data, image_2d, camera_params)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (request.name, request.frame_number, pcd_bytes, img_bytes, camera_params_json))
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

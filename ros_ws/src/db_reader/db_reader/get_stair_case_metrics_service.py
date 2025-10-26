import rclpy
from rclpy.node import Node
from builtin_interfaces.msg import Time
from every_interface_ever.srv import GetStairCaseMetrics  # Adjust pkg name
import mysql.connector
from datetime import datetime

class StairCaseMetrics(Node):
    def __init__(self):
        super().__init__('get_stair_case_metrics_service')
        self.srv = self.create_service(GetStairCaseMetrics, 'get_stair_case_metrics', self.get_stair_callback)
        self.get_logger().info('✅ GetStair service is ready.')

    def get_stair_callback(self, request, response):
        stair_id = request.id
        try:
            conn = mysql.connector.connect(
                host="mysql",
                user="stairuser",
                password="stairpass",
                database="stairs_db"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM stairs WHERE id = %s", (stair_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if not row:
                self.get_logger().warn(f"No stair found for id={stair_id}")
                return response  # return empty/default response

            # Fill the response fields
            response.metrics.id = row["id"]
            response.metrics.step_depth = float(row["step_depth"])
            response.metrics.step_height = float(row["step_height"])
            response.metrics.step_width = float(row["step_width"])
            response.metrics.slope_deg = float(row["slope_deg"])
            response.metrics.stair_angle_deg = float(row["stair_angle_deg"])
            response.metrics.pos_x = float(row["pos_x"])
            response.metrics.pos_y = float(row["pos_y"])
            response.metrics.sep_dist_parallel = float(row["sep_dist_parallel"])
            response.metrics.sep_dist_perpendicular = float(row["sep_dist_perpendicular"])
            response.metrics.anchor_point = float(row["anchor_point"])
            response.metrics.stair_parts = int(row["stair_parts"])
            response.metrics.risers = int(row["risers"])
            response.metrics.treads = int(row["treads"])

            # Convert datetime to builtin_interfaces/Time
            if isinstance(row["created_at"], datetime):
                dt = row["created_at"]
                created_at_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
                response.metrics.created_at = created_at_str

            self.get_logger().info(f"✅ Stair ID {stair_id} fetched successfully.")
            return response

        except Exception as e:
            self.get_logger().error(f"Error fetching stair data: {e}")
            return response


def main(args=None):
    rclpy.init(args=args)
    node = StairCaseMetrics()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

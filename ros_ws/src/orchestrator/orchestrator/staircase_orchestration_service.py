import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_msgs.msg import Bool
from every_interface_ever.srv import SavePointCloud
from every_interface_ever.msg import CalculatedPtMetrics
from every_interface_ever.srv import GetStairCaseMetrics 
from every_interface_ever.msg import StaircaseComplianceStatus

import datetime
import random
import string
from dataclasses import dataclass, fields, field, asdict
import requests


from typing import Dict

@dataclass
class StairCompliance:
    width_ok: bool = False
    tread_ok: bool = False
    riser_tread_relation_ok: bool = False
    stair_angle_ok: bool = False
    step_profile_ok: bool = False
    floor_marking_ok: bool = False
    parapet_height_ok: bool = False
    sphere_block_ok: bool = False
    handrail_height_ok: bool = False
    handrail_extension_ok: bool = False
    handrail_clearance_ok: bool = False

    # Optional notes for each check
    notes: Dict[str, str] = field(default_factory=dict)

    def mapToComplianceMessage(dto):
        """Convert the compliance part of the DTO to a ROS2 message"""
        msg = StaircaseComplianceStatus()
        msg.width_ok = dto.width_ok
        msg.tread_ok = dto.tread_ok
        msg.riser_tread_relation_ok = dto.riser_tread_relation_ok
        msg.stair_angle_ok = dto.stair_angle_ok
        msg.step_profile_ok = dto.step_profile_ok
        msg.floor_marking_ok = dto.floor_marking_ok
        msg.parapet_height_ok = dto.parapet_height_ok
        msg.sphere_block_ok = dto.sphere_block_ok
        msg.handrail_height_ok = dto.handrail_height_ok
        msg.handrail_extension_ok = dto.handrail_extension_ok
        msg.handrail_clearance_ok = dto.handrail_clearance_ok
        return msg


@dataclass
class StairMetricsDTO:
    pointcloud_id: int = -1
    stairs_id: int = -1
    step_depth: float = -1.0
    step_height: float = -1.0
    step_width: float = -1.0
    slope_deg: float = -1.0
    stair_angle_deg: float = -1.0
    pos_x: float = -1.0
    pos_y: float = -1.0
    sep_dist_parallel: float = -1.0
    sep_dist_perpendicular: float = -1.0
    anchor_point: float = -1.0
    stair_parts: int = -1
    risers: int = -1
    treads: int = -1
    created_at: str = "NOT_SET"
    is_filled: bool = False  # This field will be updated automatically

    def mapFromCalculatedPtMetricsMsg(self, msg):
        """Update the DTO from a ROS2 CalculatedPtMetrics message."""
        self.stairs_id = msg.id
        self.step_depth = msg.step_depth
        self.step_height = msg.step_height
        self.step_width = msg.step_width
        self.slope_deg = msg.slope_deg
        self.stair_angle_deg = msg.stair_angle_deg
        self.pos_x = msg.pos_x
        self.pos_y = msg.pos_y
        self.sep_dist_parallel = msg.sep_dist_parallel
        self.sep_dist_perpendicular = msg.sep_dist_perpendicular
        self.anchor_point = msg.anchor_point
        self.stair_parts = msg.stair_parts
        self.risers = msg.risers
        self.treads = msg.treads
        self.created_at = msg.created_at

    @staticmethod
    def to_calculated_pt_metrics_msg(dto):
        """Convert a StairMetricsDTO instance to a ROS2 CalculatedPtMetrics message."""
        msg = CalculatedPtMetrics()
        msg.id = dto.stairs_id
        msg.step_depth = dto.step_depth
        msg.step_height = dto.step_height
        msg.step_width = dto.step_width
        msg.slope_deg = dto.slope_deg
        msg.stair_angle_deg = dto.stair_angle_deg
        msg.pos_x = dto.pos_x
        msg.pos_y = dto.pos_y
        msg.sep_dist_parallel = dto.sep_dist_parallel
        msg.sep_dist_perpendicular = dto.sep_dist_perpendicular
        msg.anchor_point = dto.anchor_point
        msg.stair_parts = dto.stair_parts
        msg.risers = dto.risers
        msg.treads = dto.treads
        msg.created_at = dto.created_at
        return msg


    def check_if_filled(self) -> bool:
        """
        Checks all fields except is_filled itself.
        Returns True if all fields have non-placeholder values.
        """
        for f in fields(self):
            if f.name == "is_filled":
                continue
            value = getattr(self, f.name)
            if (isinstance(value, int) and value == -1) or \
               (isinstance(value, float) and value == -1.0) or \
               (isinstance(value, str) and value == "NOT_SET"):
                self.is_filled = False
                return False
            
        self.is_filled = True
        return True


class StaircaseOrchestrationService(Node):
    def __init__(self):
        super().__init__('staircase_orchestration_service')

        self.data: StairMetricsDTO
        self.compliance: StairCompliance
        self.data_ready = False
        self.algorithm_url = 'http://localhost:8001/run'
        self.compliance_calculator_url = 'http://localhost:8000/check'
        # Subscribe to the button topics:
        self.savePcSubscription = self.create_subscription(
            String,
            '/save_pt_request',
            self.save_pc_requested,
            10
        )
        self.saveAndProcessPcSubscription = self.create_subscription(
            String,
            '/save_and_process_pt_request',
            self.save_and_process_pc_requested,
            10
        )
        
        # publishers to send data to UI:
        self.stairCasePublisher = self.create_publisher(CalculatedPtMetrics, '/stairs_calculated_metrics', 10)
        # publisher to send success on point_cloud_save
        self.pointCloudSaverPublisher = self.create_publisher(Bool, '/pc_saved_response', 10)
        # publish compliance status message to UI:
        self.stairCaseComplianceStatusPublisher = self.create_publisher(StaircaseComplianceStatus, '/stairs_compliance_status', 10)




        #service clients for saving pointcloud and triggering processing pipeline:
        self.savePointCloudClient = self.create_client(SavePointCloud, 'save_pointcloud')
        if not self.savePointCloudClient.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Service /save_pointcloud not available')
            return
        
        self.getStaircaseMetricsClient = self.create_client(GetStairCaseMetrics, 'get_stair_case_metrics')
        if not self.getStaircaseMetricsClient.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Service /get_stair_case_metrics not available')
            return


        self.latest_msg = None
        self.get_logger().info("StaircaseOrchestrationService ready. Waiting for get_staircase_measurements requests...")

    def save_pc_requested(self, msg):
        """
        triggers necessary services to save point cloud to database
        """
        future = self.save_point_cloud_helper()
                # Attach a local callback to handle the response
        def callback(fut):
            try:
                response = fut.result()
                self.get_logger().info(f"Point cloud saved successfully. pointcloud_id: {response.pointcloud_id}")
                
                self.data = StairMetricsDTO(pointcloud_id=response.pointcloud_id)

                savedMsg = Bool()
                savedMsg.data = response.success
                self.pointCloudSaverPublisher.publish(savedMsg)
            except Exception as e:
                self.get_logger().error(f"Service call failed: {e}")

        future.add_done_callback(callback)

    def save_point_cloud_helper(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Random 6-character string
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        pc_name = f"pc_{timestamp}_{rand_str}.pcd"

        request = SavePointCloud.Request()
        request.frame_number = 1
        request.name = pc_name
        return self.savePointCloudClient.call_async(request)

    def save_and_process_pc_requested(self, msg):
        """
        triggers save point cloud pipeline, then trigger measurement pipeline to generate metrics, 
        then triggers db_reader pipeline to fetch those metrics from database and publishes them to UI topic.
        Also calls an http server to check if the calculated metrics are compliant with whats set out as the standard.
        """
        future = self.save_point_cloud_helper()
                # Attach a local callback to handle the response
        def saveCallback(fut):
            try:
                response = fut.result()
                self.get_logger().info(f"Point cloud saved successfully. pointcloud_id: {response.pointcloud_id}")
                
                self.data = StairMetricsDTO(pointcloud_id=response.pointcloud_id)
                savedMsg = Bool()
                savedMsg.data = response.success
                self.pointCloudSaverPublisher.publish(savedMsg)
                success = self.trigger_processing_pipeline_helper(pointcloud_id=self.data.pointcloud_id)
                if (success):
                    future2 = self.get_metrics_helper(pointcloud_id=self.data.pointcloud_id)
                    def getMetricsCallback(fut):
                        try:
                            
                            response = fut.result()                            
                            self.data.mapFromCalculatedPtMetricsMsg(response.metrics)
                            if (self.data.check_if_filled()):
                                metricsMessage = StairMetricsDTO.to_calculated_pt_metrics_msg(self.data)
                                self.get_logger().info(f"publishing metrics to UI")
                                self.stairCasePublisher.publish(metricsMessage)

                                self.get_logger().info(f"publishing metrics to UI")
                                self.get_compliance_metrics_helper()
                                complianceStatusMessage = StairCompliance.mapToComplianceMessage(self.compliance)
                                self.stairCaseComplianceStatusPublisher.publish(complianceStatusMessage)

                        except Exception as e:
                            self.get_logger().error(f"Service call failed: {e}")

                    future2.add_done_callback(getMetricsCallback)
                else:
                    self.get_logger().error(f"trigger_processing_pipeline failed")
                
            except Exception as e:
                self.get_logger().error(f"Service call failed: {e}")

        future.add_done_callback(saveCallback)

    def trigger_processing_pipeline_helper(self, pointcloud_id):
        # JSON payload
        payload = {
            "pointcloud_id": pointcloud_id,
            "enable_viewer": False
        }

        # Send POST request with JSON body
        response = requests.post(self.algorithm_url, json=payload)

        # Check response
        if response.status_code == 200:
            
            self.get_logger().info(f"processing algorithm responded with: {response.json()}")  # parse JSON response if any
            return response.json()['success']
        else:
            self.get_logger().error(f"Error: {response.status_code} {response.text}")
    
    def get_metrics_helper(self, pointcloud_id):
        request = GetStairCaseMetrics.Request()
        request.id = pointcloud_id
        self.get_logger().info(f"calling get_stair_case_metrics")

        return self.getStaircaseMetricsClient.call_async(request)

    def get_compliance_metrics_helper(self):
        self.compliance = StairCompliance()
        payload = asdict(self.data)
        response = requests.post(self.compliance_calculator_url, json=payload)
        # Update the compliance object with the API response
        if response.status_code == 200:
            data = response.json()
            # This ensures **all fields in compliance** are updated
            for key, value in data.get("compliance", {}).items():
                if hasattr(self.compliance, key):
                    setattr(self.compliance, key, value)
            # Optionally update notes too
            self.compliance.notes = data.get("notes", {})
        else:
            self.get_logger().error(f"Compliance API request failed: {response.status_code} {response.text}")
        self.get_logger().info(f"{self.compliance}")

def main(args=None):
    rclpy.init(args=args)
    node = StaircaseOrchestrationService()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

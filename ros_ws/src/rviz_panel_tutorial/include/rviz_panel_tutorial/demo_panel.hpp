/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2024, Metro Robots
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of Metro Robots nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *********************************************************************/

/* Author: David V. Lu!! */

#ifndef RVIZ_PANEL_TUTORIAL__DEMO_PANEL_HPP_
#define RVIZ_PANEL_TUTORIAL__DEMO_PANEL_HPP_

#include <QLabel>
#include <QPushButton>
#include <QTableWidget>
#include <rviz_common/panel.hpp>
#include <rviz_common/ros_integration/ros_node_abstraction_iface.hpp>
#include <std_msgs/msg/string.hpp>
#include "every_interface_ever/msg/calculated_pt_metrics.hpp"
#include "every_interface_ever/msg/staircase_compliance_status.hpp"


namespace rviz_panel_tutorial
{
class DemoPanel : public rviz_common::Panel
{
  Q_OBJECT
public:
  explicit DemoPanel(QWidget * parent = 0);
  ~DemoPanel() override;

  void onInitialize() override;

protected:
  std::shared_ptr<rviz_common::ros_integration::RosNodeAbstractionIface> node_ptr_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr save_and_process_pt_publisher_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr save_pt_publisher_;

  rclcpp::Subscription<every_interface_ever::msg::CalculatedPtMetrics>::SharedPtr subscriber_;
  rclcpp::Subscription<every_interface_ever::msg::StaircaseComplianceStatus>::SharedPtr compliance_subscriber_;


  void topicCallback(const std_msgs::msg::String& msg);

  QLabel * label_;
  QPushButton * save_pt_button_;
  QPushButton * process_pt_button_;
  QTableWidget * table_;
  QTableWidget * table2_;

private Q_SLOTS:
  void ptSaverButtonActivated();
  void ptStoreAndProcessbuttonActivated();
  void updateTable(int id, float step_depth, float step_height, float step_width, int stair_parts, int risers, int treads, std::string created_at);
  void setTableToDefault();

  void updateComplianceTable(bool width_ok, bool tread_ok, bool riser_tread_relation_ok);
  void setComplianceTableToDefault();

Q_SIGNALS:
  void newData(int id, float step_depth, float step_height, float step_width, int stair_parts, int risers, int treads, std::string created_at);
  void clearTable();
  void newComplianceData(bool width_ok, bool tread_ok, bool riser_tread_relation_ok);
  void clearComplianceTable();
};

}  // namespace rviz_panel_tutorial

#endif  // RVIZ_PANEL_TUTORIAL__DEMO_PANEL_HPP_

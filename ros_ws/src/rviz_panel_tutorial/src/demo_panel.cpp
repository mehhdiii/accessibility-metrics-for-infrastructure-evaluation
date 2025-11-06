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

#include <QVBoxLayout>
#include <QHeaderView>
#include <rviz_common/display_context.hpp>
#include <rviz_panel_tutorial/demo_panel.hpp>

namespace rviz_panel_tutorial
{
DemoPanel::DemoPanel(QWidget * parent) : Panel(parent)
{
  // Create a label and a button:
  const auto layout = new QVBoxLayout(this);
  label_ = new QLabel("PCL controls");
  save_pt_button_ = new QPushButton("Save pointcloud to database");
  process_pt_button_ = new QPushButton("Save and process pointCloud");
  layout->addWidget(label_);
  layout->addWidget(save_pt_button_);
  layout->addWidget(process_pt_button_);


  //create table and attach to layout:
  table_ = new QTableWidget(8, 2);
  table_->setHorizontalHeaderLabels({"Field", "Value"});
  table_->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
  QStringList labels = {"ID", "Step Depth", "Step Height", "Step Width", "Stair Parts", "Risers", "Treads", "CreatedAt"};
  for (int i = 0; i < 8; ++i) {
    table_->setItem(i, 0, new QTableWidgetItem(labels[i]));
    table_->setItem(i, 1, new QTableWidgetItem("—"));
  }
  layout->addWidget(table_);

  table2_ = new QTableWidget(3, 2);
  table2_->setHorizontalHeaderLabels({"Field", "Value"});
  table2_->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
  QStringList labels2 = {"width ok", "tread ok", "riser tread relation ok"};
  for (int i = 0; i < 3; ++i) {
    table2_->setItem(i, 0, new QTableWidgetItem(labels2[i]));
    table2_->setItem(i, 1, new QTableWidgetItem("—"));
  }
  layout->addWidget(table2_);


  // Connect the event of when the button is released to trigger the callback,
  QObject::connect(save_pt_button_, &QPushButton::released, this, &DemoPanel::ptSaverButtonActivated);
  QObject::connect(process_pt_button_, &QPushButton::released, this, &DemoPanel::ptStoreAndProcessbuttonActivated);
  QObject::connect(this, &DemoPanel::newData, this, &DemoPanel::updateTable);
  QObject::connect(this, &DemoPanel::clearTable, this, &DemoPanel::setTableToDefault);

  QObject::connect(this, &DemoPanel::clearComplianceTable, this, &DemoPanel::setComplianceTableToDefault);
  QObject::connect(this, &DemoPanel::newComplianceData, this, &DemoPanel::updateComplianceTable);



}

DemoPanel::~DemoPanel() = default;

void DemoPanel::onInitialize()
{
  // Access the abstract ROS Node and
  // in the process lock it for exclusive use until the method is done.
  node_ptr_ = getDisplayContext()->getRosNodeAbstraction().lock();

  // Get a pointer to the familiar rclcpp::Node for making subscriptions/publishers
  // (as per normal rclcpp code)
  rclcpp::Node::SharedPtr node = node_ptr_->get_raw_node();
  save_pt_publisher_ = node->create_publisher<std_msgs::msg::String>("/save_pt_request", 10);
  save_and_process_pt_publisher_ = node->create_publisher<std_msgs::msg::String>("/save_and_process_pt_request", 10);

  // Subscriber for updates
  subscriber_ = node->create_subscription<every_interface_ever::msg::CalculatedPtMetrics>(
    "/stairs_calculated_metrics",
    10,
    [this](const every_interface_ever::msg::CalculatedPtMetrics::SharedPtr msg) {
      // Don't modify UI here directly, instead emit signal
      emit newData(msg->id, msg->step_depth, msg->step_height, msg->step_width, msg->stair_parts, msg->risers, msg->treads, msg->created_at);
    });

  compliance_subscriber_ = node->create_subscription<every_interface_ever::msg::StaircaseComplianceStatus>(
    "/stairs_compliance_status",
    10,
    [this](const every_interface_ever::msg::StaircaseComplianceStatus::SharedPtr msg) {
      // Don't modify UI here directly, instead emit signal
      emit newComplianceData(msg->width_ok, msg->tread_ok, msg->riser_tread_relation_ok);
    });
}

// When the widget's button is pressed, this callback is triggered,
void DemoPanel::ptSaverButtonActivated()
{
  emit clearTable();
  auto message = std_msgs::msg::String();
  message.data = "Save point cloud";
  save_pt_publisher_->publish(message);
}

void DemoPanel::ptStoreAndProcessbuttonActivated()
{
  auto message = std_msgs::msg::String();
  message.data = "Save and process point cloud";
  save_and_process_pt_publisher_->publish(message);
}

void DemoPanel::updateTable(int id, float step_depth, float step_height, float step_width, int stair_parts, int risers, int treads, std::string created_at)
{
  table_->item(0, 1)->setText(QString::number(id));
  table_->item(1, 1)->setText(QString::number(step_depth));
  table_->item(2, 1)->setText(QString::number(step_height));
  table_->item(3, 1)->setText(QString::number(step_width));
  table_->item(4, 1)->setText(QString::number(stair_parts));
  table_->item(5, 1)->setText(QString::number(risers));
  table_->item(6, 1)->setText(QString::number(treads));
  table_->item(7, 1)->setText(QString::fromStdString(created_at));

}

void DemoPanel::setTableToDefault() {
  table_->item(0, 1)->setText(QString::fromStdString("-"));
  table_->item(1, 1)->setText(QString::fromStdString("-"));
  table_->item(2, 1)->setText(QString::fromStdString("-"));
  table_->item(3, 1)->setText(QString::fromStdString("-"));
  table_->item(4, 1)->setText(QString::fromStdString("-"));
  table_->item(5, 1)->setText(QString::fromStdString("-"));
  table_->item(6, 1)->setText(QString::fromStdString("-"));
  table_->item(7, 1)->setText(QString::fromStdString("-"));
}


void DemoPanel::updateComplianceTable(bool width_ok, bool tread_ok, bool riser_tread_relation_ok) {
  table2_->item(0, 1)->setText(width_ok ? "✔" : "✘");
  table2_->item(1, 1)->setText(tread_ok ? "✔" : "✘");
  table2_->item(2, 1)->setText(riser_tread_relation_ok ? "✔" : "✘");
}

void DemoPanel::setComplianceTableToDefault() {
  table2_->item(0, 1)->setText(QString::fromStdString("-"));
  table2_->item(1, 1)->setText(QString::fromStdString("-"));
  table2_->item(2, 1)->setText(QString::fromStdString("-"));
}

}  // namespace rviz_panel_tutorial

#include <pluginlib/class_list_macros.hpp>
PLUGINLIB_EXPORT_CLASS(rviz_panel_tutorial::DemoPanel, rviz_common::Panel)

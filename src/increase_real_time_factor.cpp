// Copyright (c) 2022 PAL Robotics S.L. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <ros/ros.h>
#include <gazebo_msgs/GetPhysicsProperties.h>
#include <gazebo_msgs/SetPhysicsProperties.h>

int main(int argc, char** argv)
{
  ros::init(argc, argv, "increase_real_time_factor");
  ros::NodeHandle nh("~");

  double real_time_factor = 0.0;
  nh.param<double>("real_time_factor", real_time_factor, 1.0);

  ros::ServiceClient get_properties_srv =
      nh.serviceClient<gazebo_msgs::GetPhysicsProperties>("/gazebo/get_physics_properties");
  ros::ServiceClient set_properties_srv =
      nh.serviceClient<gazebo_msgs::SetPhysicsProperties>("/gazebo/set_physics_properties");

  if ((!get_properties_srv.waitForExistence(ros::Duration(10.0))) ||
      (!set_properties_srv.waitForExistence(ros::Duration(10.0))))
  {
    ROS_ERROR("Gazebo set/get physics properties are not available");
  }

  gazebo_msgs::GetPhysicsProperties get_msg;

  if(!get_properties_srv.call(get_msg))
  {
      ROS_ERROR("Error calling /gazebo/get_physics_properties");
  }

  ROS_INFO_STREAM("Updating to a real time factor of " << real_time_factor);
  gazebo_msgs::SetPhysicsProperties set_msg;
  set_msg.request.time_step = get_msg.response.time_step;
  set_msg.request.max_update_rate = get_msg.response.max_update_rate * real_time_factor;
  set_msg.request.gravity = get_msg.response.gravity;
  set_msg.request.ode_config = get_msg.response.ode_config;

  if(!set_properties_srv.call(set_msg))
  {
      ROS_ERROR("Error calling /gazebo/get_physics_properties");
  }

  if(!set_msg.response.success)
      ROS_ERROR_STREAM("Error updating physics properties: " << set_msg.response.status_message);

  ROS_INFO("Physics properties updated!");

  return (0);
}

#include <gazebo_msgs/LinkStates.h>
#include <gtest/gtest.h>
#include <ros/ros.h>
namespace pal {

TEST(TestServer, test) {
  ros::NodeHandle nh;
  bool sim_time = false;
  ASSERT_TRUE(nh.getParam("/use_sim_time", sim_time));
  ASSERT_TRUE(sim_time);

  gazebo_msgs::LinkStatesConstPtr msg =
      ros::topic::waitForMessage<gazebo_msgs::LinkStates>(
          "/gazebo/link_states", nh, ros::Duration(10.0));

  ASSERT_TRUE(msg.get());
}

} // namespace pal

int main(int argc, char **argv) {
  ros::init(argc, argv, "test_run_gazebo_server");
  ros::NodeHandle nh;
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

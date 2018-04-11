cmake_minimum_required(VERSION 2.8.3)
project(pal_gazebo_worlds)

find_package(catkin REQUIRED)

catkin_package()

foreach(dir launch models worlds urdf meshes)
    install(DIRECTORY ${dir}/
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)

if(CATKIN_ENABLE_TESTING)
  find_package(rostest REQUIRED)
  find_package(roscpp REQUIRED)
  find_package(gazebo_msgs REQUIRED)
  include_directories(SYSTEM ${roscpp_INCLUDE_DIRS} ${gazebo_msgs_INCLUDE_DIRS})

  add_rostest_gtest(run_gazebo_server-test test/run_gazebo_server.test test/test_run_gazebo_server.cpp)
  target_link_libraries(run_gazebo_server-test ${roscpp_LIBRARIES})
endif(CATKIN_ENABLE_TESTING)

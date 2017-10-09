cmake_minimum_required(VERSION 2.8.3)
project(pal_gazebo_worlds)

find_package(catkin REQUIRED)

catkin_package()

foreach(dir config launch models worlds)
    install(DIRECTORY ${dir}/
        DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/${dir})
endforeach(dir)

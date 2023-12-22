# Copyright (c) 2022 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from os import environ, pathsep

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    ExecuteProcess,
    OpaqueFunction
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def start_gzserver(context, *args, **kwargs):
    pkg_path = get_package_share_directory('pal_gazebo_worlds')
    priv_pkg_path = ''
    try:
        priv_pkg_path = get_package_share_directory('pal_gazebo_worlds_private')
    except Exception:
        pass

    world_name = LaunchConfiguration('world_name').perform(context)

    world = ''
    if os.path.exists(os.path.join(priv_pkg_path, 'worlds', world_name + '.world')):
        world = os.path.join(priv_pkg_path, 'worlds', world_name + '.world')
    elif os.path.exists(os.path.join(pkg_path, 'worlds', world_name + '.world')):
        world = os.path.join(pkg_path, 'worlds', world_name + '.world')

    params_file = PathJoinSubstitution(
        substitutions=[pkg_path, 'config', 'gazebo_params.yaml'])

    start_gazebo_server_cmd = ExecuteProcess(
        cmd=['gzserver', '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so', world,
             '--ros-args', '--params-file', params_file],
        output='screen')

    return [start_gazebo_server_cmd]


def generate_launch_description():
    # Attempt to find pal_gazebo_worlds_private, use pal_gazebo_worlds otherwise
    try:
        priv_pkg_path = get_package_share_directory(
            'pal_gazebo_worlds_private')
        model_path = os.path.join(priv_pkg_path, 'models') + pathsep
        resource_path = priv_pkg_path + pathsep
    except Exception:
        model_path = ''
        resource_path = ''

    # Add pal_gazebo_worlds path
    pkg_path = get_package_share_directory('pal_gazebo_worlds')
    model_path += os.path.join(pkg_path, 'models')
    resource_path += pkg_path

    if 'GAZEBO_MODEL_PATH' in environ:
        model_path += pathsep+environ['GAZEBO_MODEL_PATH']
    if 'GAZEBO_RESOURCE_PATH' in environ:
        resource_path += pathsep+environ['GAZEBO_RESOURCE_PATH']

    declare_world_name = DeclareLaunchArgument(
        'world_name', default_value='',
        description="Specify world name, we'll convert to full path"
    )

    start_gazebo_server_cmd = OpaqueFunction(function=start_gzserver)

    start_gazebo_client_cmd = ExecuteProcess(
        cmd=['gzclient'], output='screen')

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(declare_world_name)

    ld.add_action(SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path))
    # Using this prevents shared library from being found
    # ld.add_action(SetEnvironmentVariable('GAZEBO_RESOURCE_PATH', resource_path))

    ld.add_action(start_gazebo_server_cmd)
    ld.add_action(start_gazebo_client_cmd)

    return ld

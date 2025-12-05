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
import pathlib
from os import environ, pathsep

from ament_index_python.packages import get_package_share_directory, get_package_prefix

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    SetEnvironmentVariable,
    ExecuteProcess,
    OpaqueFunction,
)
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_pal.robot_arguments import CommonArgs


def get_pkg_path():
    return pathlib.Path(get_package_share_directory('pal_gazebo_worlds'))


def get_private_pkg_path():
    priv_pkg_path = pathlib.Path('')
    try:
        priv_pkg_path = pathlib.Path(get_package_share_directory('pal_gazebo_worlds_private'))
    except Exception:
        print("Private gazebo world package not found.")
    return priv_pkg_path


def get_world_name(context):
    return LaunchConfiguration('world_name').perform(context)


def find_world(world_name, priv_pkg_path, pkg_path, extension):
    world = pathlib.Path(world_name)

    pkg_world_path = pkg_path / 'worlds' / (world_name + extension)
    priv_pkg_world_path = priv_pkg_path / 'worlds' / (world_name + extension)
    if priv_pkg_world_path.is_file():
        world = str(priv_pkg_world_path)
    elif pkg_world_path.is_file():
        world = str(pkg_world_path)
    else:
        print("World file not found.")
        world = str('')
    return world


def start_gazebo_classic(context, *args, **kwargs):
    pkg_path = get_pkg_path()
    priv_pkg_path = get_private_pkg_path()
    world_name = get_world_name(context)
    world = find_world(world_name, pkg_path, priv_pkg_path, '.world')
    gazebo_clock_rate = LaunchConfiguration('clock_rate').perform(context)

    # Command to start the gazebo server.
    gazebo_server_cmd_line = [
        'gzserver', '-s', 'libgazebo_ros_init.so',
        '-s', 'libgazebo_ros_factory.so', world,
        '--ros-args', '--param', f"publish_rate:={gazebo_clock_rate}"]
    # Start the server under the gdb framework.
    debug = LaunchConfiguration('debug').perform(context)
    if debug == 'True':
        gazebo_server_cmd_line = (
            ['xterm', '-e', 'gdb', '-ex', 'run', '--args'] +
            gazebo_server_cmd_line
        )

    # Start the gazebo classic server.
    start_gazebo_classic_server_cmd = ExecuteProcess(
        cmd=gazebo_server_cmd_line, output='screen')

    # Start the gazebo classic Gui.
    start_gazebo_classic_client_cmd = ExecuteProcess(
        cmd=['gzclient'], output='screen',
        condition=IfCondition(LaunchConfiguration('gzclient'))
    )

    return [start_gazebo_classic_server_cmd, start_gazebo_classic_client_cmd]


def start_gz(context, *args, **kwargs):
    pkg_path = get_pkg_path()
    priv_pkg_path = get_private_pkg_path()
    world_name = get_world_name(context)
    world = find_world(world_name, pkg_path, priv_pkg_path, '.sdf')

    # Command to start the gazebo server.
    gazebo_server_cmd_line = ['ign', 'gazebo', '-r', '-v', '4', '-s', world]
    # Start the server under the gdb framework.
    debug = LaunchConfiguration('debug').perform(context)
    if debug == 'True':
        gazebo_server_cmd_line = (
            ['xterm', '-e'] +
            gazebo_server_cmd_line
        )
    start_gazebo_server_cmd = ExecuteProcess(
        cmd=gazebo_server_cmd_line, output='screen')

    start_gazebo_client_cmd = ExecuteProcess(
        cmd=['ign', 'gazebo', '-v', '4', '-g'], output='screen',
        condition=IfCondition(LaunchConfiguration('gzclient'))
    )

    return [start_gazebo_server_cmd, start_gazebo_client_cmd]


def start_gazebo(context, *args, **kwargs):
    actions = []

    gazebo_version = LaunchConfiguration('gazebo_version').perform(context)

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

    if gazebo_version == 'gazebo':
        if 'GZ_SIM_RESOURCE_PATH' in environ:
            resource_path += pathsep+environ['GZ_SIM_RESOURCE_PATH']

        system_plugin_path = os.path.join(get_package_prefix('gz_ros2_control'), 'lib')
        if 'GZ_SIM_SYSTEM_PLUGIN_PATH' in environ:
            system_plugin_path += pathsep + environ['GZ_SIM_SYSTEM_PLUGIN_PATH']

        actions.append(SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', resource_path))
        actions.append(SetEnvironmentVariable('GZ_SIM_SYSTEM_PLUGIN_PATH', system_plugin_path))
        actions.append(OpaqueFunction(function=start_gz))
    elif gazebo_version == 'classic':
        if 'GAZEBO_MODEL_PATH' in environ:
            model_path += pathsep+environ['GAZEBO_MODEL_PATH']
        if 'GAZEBO_RESOURCE_PATH' in environ:
            resource_path += pathsep+environ['GAZEBO_RESOURCE_PATH']

        actions.append(SetEnvironmentVariable('GAZEBO_MODEL_PATH', model_path))
        # Using this prevents shared library from being found
        # actions.append(SetEnvironmentVariable('GAZEBO_RESOURCE_PATH', resource_path))
        actions.append(OpaqueFunction(function=start_gazebo_classic))
    else:
        actions.append(ExecuteProcess(cmd=[
            'echo', 'The given version of gazebo [{}] is wrong. '.format(gazebo_version) +
            'Should be \'classic\' or \'gazebo\''
        ], output='screen'))

    return actions


def generate_launch_description():
    declare_world_name = DeclareLaunchArgument(
        'world_name', default_value='',
        description="Specify world name, we'll convert to full path",
    )
    declare_debug = DeclareLaunchArgument(
        'debug', default_value='False',
        choices=['True', 'False'],
        description='If debug start the gazebo world into a gdb session in an xterm terminal',
    )
    declare_clock_rate = DeclareLaunchArgument(
        'clock_rate', default_value='200.0',
        description='The rate at which the gazebo clock needs to be published!'
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(declare_debug)
    ld.add_action(declare_world_name)
    ld.add_action(declare_clock_rate)
    ld.add_action(CommonArgs.gzclient)
    ld.add_action(CommonArgs.gazebo_version)

    ld.add_action(OpaqueFunction(function=start_gazebo))

    return ld

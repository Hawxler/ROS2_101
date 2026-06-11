from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare

import os

def generate_launch_description():
    pkg_share = FindPackageShare('r1_desc_pkg1').find('r1_desc_pkg1')

    urdf_file = os.path.join(
        pkg_share,
        'urdf',
        'robot1.urdf.xacro'
    )

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_file]),
        value_type=str
    )

    robot_description = {
        'robot_description': robot_description_content
    }

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable='robot_state_publisher',
        parameters=[robot_description],
        output='screen'
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen'
    )

    return LaunchDescription([
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        rviz_node
    ])
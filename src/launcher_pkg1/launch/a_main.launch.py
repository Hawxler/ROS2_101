# 다른 론치파일 포함 연습용: a_pubber01.launch.py + a_turtlesim01.launch.py
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():
    node1_turtle = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('launcher_pkg1'),
                'launch',
                'a_turtlesim01.launch.py'
            )
        )
    )

    node2_pubber = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('launcher_pkg1'),
                'launch',
                'a_pubber01.launch.py'
            )
        )
    )

    my_launch = LaunchDescription()
    my_launch.add_action(node1_turtle)
    my_launch.add_action(node2_pubber)

    return my_launch
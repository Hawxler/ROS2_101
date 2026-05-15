# 다른 론치파일 포함 연습용: pubber1.py만 구동하는 론치파일
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='launcher_pkg1',
            executable='pubber1',
            output='screen'
        )
    ])
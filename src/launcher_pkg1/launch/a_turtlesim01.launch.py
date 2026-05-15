# 다른 론치파일 포함 연습용: 터틀심만 구동하는 론치파일
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        )
    ])
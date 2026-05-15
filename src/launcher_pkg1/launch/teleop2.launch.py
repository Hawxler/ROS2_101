# 네임스페이스가 다를 때 remappings를 하는 경우
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            namespace='turtlesim1',
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),
        Node(
            namespace='hawx_name1',
            package='launcher_pkg1',
            executable='pubber1',
            output='screen',
            remappings=[
                ('/hawx_name1/turtle1/cmd_vel', 
                 '/turtlesim1/turtle1/cmd_vel')
            ]
        )
    ])
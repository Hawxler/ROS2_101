from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            namespace='turtlesim1', #/turtlesim1/turtlesim_node1
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),
        Node(
            namespace='turtlesim1', #/turtlesim1/pubber_node1
            package='launcher_pkg1',
            executable='pubber1', #엔트리 포인트명
            output='screen',
        )
    ])
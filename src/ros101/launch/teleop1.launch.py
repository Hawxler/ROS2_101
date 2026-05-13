from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            namespace='turtlesim1', #"/turtlesim1/노드명"
            package='turtlesim',
            executable='turtlesim_node',
            output='screen'
        ),
        Node(
            namespace='pubber1_launcher', #"/pubber1_launcher/노드명"
            package='ros101',
            executable='t_pub_node1',
            output='screen'
        )
    ])
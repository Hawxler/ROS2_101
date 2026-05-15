# add_action() + 파라미터 추가
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    my_launch = LaunchDescription()

    node1_turtlesim = Node(
        # namespace="ttt1",
        package='turtlesim',
        executable='turtlesim_node',
        output='screen',
        parameters=[
            {"background_r": 40},
            {"background_g": 200},
            {"background_b": 200}
        ]
    )

    node2_pubber1 = Node(
        # namespace="ppp1",
        package="launcher_pkg1",
        executable="pubber1",
        output="screen",
        # remappings=[
        #     ('/ppp1/turtle1/cmd_vel', '/ttt1/turtle1/cmd_vel')
        # ]
    )

    my_launch.add_action(node1_turtlesim)
    my_launch.add_action(node2_pubber1)

    return my_launch
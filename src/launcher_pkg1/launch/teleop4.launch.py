# teleop3.launch.py + 로그 출력 + 3초 딜레이 후 실행
from launch import LaunchDescription
from launch_ros.actions import Node
# Log 출력
from launch.actions import LogInfo
# 시간 지연 후 노드 실행
from launch.actions import TimerAction

def generate_launch_description():
    my_launch = LaunchDescription()

    node1_turtlesim = Node(
        namespace="t1",
        package='turtlesim',
        executable='turtlesim_node',
        output='screen',
        parameters=[
            {"background_r": 30},
            {"background_g": 200},
            {"background_b": 200}
        ]
    )

    node2_pubber1 = Node(
        namespace="hawx_pub1",
        package='launcher_pkg1',
        executable="pubber1",
        output="screen",
        remappings=[
            ('/turtle1/cmd_vel', 
             '/t1/turtle1/cmd_vel')
        ]
    )

    my_launch.add_action(node1_turtlesim)
    # log 출력
    my_launch.add_action(
        LogInfo(msg='Start this Launch')
    )
    # Timer 적용
    my_launch.add_action(
        TimerAction(
            period=3.0,
            actions=[
                node2_pubber1
            ]
        )
    )

    return my_launch

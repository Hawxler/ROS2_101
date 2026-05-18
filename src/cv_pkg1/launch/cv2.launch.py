# 론치 파일 + 외부 파일
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    params_file = os.path.join(
        get_package_share_directory('cv_pkg1'),
        'config',
        'size1.yaml'
    )

    img_pub_node = Node(
        package='cv_pkg1',
        executable='img_pub2',
        output='screen',
        parameters=[params_file]
    )

    my_launch = LaunchDescription()
    my_launch.add_action(img_pub_node)

    return my_launch


# 또는 아래처럼 써도 됨.
# 일반적인 launch 파일 + 파라미터 파일 불러오기
"""
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution

def generate_launch_description():
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'parmas_file',
            defaut_value=PathJoinSubstitution([
                FindPackageShare('cv_pkg1'),
                'config',
                'size.yaml'
            ])
        ),

        Node(
            package='cv_pkg1',
            executable='img_pub1',
            output='screen',
            parameters=[
                params_file
            ]
        )
    ])
"""
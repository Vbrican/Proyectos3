from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('diccionario', default_value='5X5_100'),
        Node(package='g14_prii3_aruco', executable='detectar_aruco_ros',
             parameters=[{'diccionario': LaunchConfiguration('diccionario'), 'use_sim_time': True}]),
        Node(package='g14_prii3_aruco', executable='autonomous_navigation',
             parameters=[{'use_sim_time': True}]),
    ])

# Igual que el launch de simulacion, pero en robot real: use_sim_time=False.
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='g14_prii3_move_jetbot',
            executable='draw_number',
            name='draw_number',
            output='screen',
            parameters=[{'use_sim_time': False, 'usar_lidar': True}],
        ),
        Node(
            package='g14_prii3_move_jetbot',
            executable='collision_avoidance',
            name='detector_colisiones',
            output='screen',
            parameters=[{'use_sim_time': False}],
        ),
    ])

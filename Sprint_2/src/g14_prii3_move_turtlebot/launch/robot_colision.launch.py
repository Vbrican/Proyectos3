# Lanza el dibujo del 14 y el detector de obstaculos en Gazebo.
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Es el UNICO nodo que envia ordenes /cmd_vel.
        Node(
            package='g14_prii3_move_turtlebot',
            executable='draw_number',
            name='draw_number',
            output='screen',
            parameters=[{'use_sim_time': True, 'usar_lidar': True}],
        ),
        # Este nodo solamente lee /scan y publica /obstaculo_detectado.
        Node(
            package='g14_prii3_move_turtlebot',
            executable='collision_avoidance',
            name='detector_colisiones',
            output='screen',
            parameters=[{'use_sim_time': True}],
        ),
    ])
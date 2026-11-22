import math
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


def main():
    rclpy.init()
    nodo = Node('predefined_navigation')
    cliente = ActionClient(nodo, NavigateToPose, '/navigate_to_pose')

    objetivo = NavigateToPose.Goal()
    objetivo.pose.header.frame_id = 'map'
    objetivo.pose.header.stamp = nodo.get_clock().now().to_msg()
    objetivo.pose.pose.position.x = -1.194
    objetivo.pose.pose.position.y = 7.200

    yaw = 0.9495
    objetivo.pose.pose.orientation.z = math.sin(yaw / 2)
    objetivo.pose.pose.orientation.w = math.cos(yaw / 2)

    cliente.wait_for_server()
    futuro = cliente.send_goal_async(objetivo)
    rclpy.spin_until_future_complete(nodo, futuro)

    if futuro.result().accepted:
        resultado = futuro.result().get_result_async()
        rclpy.spin_until_future_complete(nodo, resultado)
        if resultado.result().status == GoalStatus.STATUS_SUCCEEDED:
            print('Destino alcanzado')
        else:
            print('No se ha podido llegar')
    else:
        print('Destino rechazado')

    nodo.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

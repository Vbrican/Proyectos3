import json
from math import sin, cos

import rclpy
from rclpy.node import Node
from rclpy.time import Time
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String
from tf2_ros import Buffer, TransformListener


PUERTA = (3.263, 1.687, 2.0)
DESTINOS = {
    5: (-1.194, 7.200, 0.9495),
    17: (3.729, 14.077, -1.5425),
    6: (3.796, 11.707, -1.5425),
}


class NavegacionAruco(Node):
    def __init__(self):
        super().__init__('autonomous_navigation')
        self.nav = ActionClient(self, NavigateToPose, '/navigate_to_pose')
        self.tf = Buffer()
        self.listener = TransformListener(self.tf, self)
        self.suscriptor = self.create_subscription(String, '/aruco_detectados', self.leer, 10)
        self.temporizador = self.create_timer(1.0, self.iniciar)
        self.estado = 'inicio'
        self.anterior = None
        self.veces = 0
        self.objetivo = None

    def iniciar(self):
        if self.estado == 'inicio' and self.nav.server_is_ready() and \
                self.tf.can_transform('map', 'base_link', Time()):
            self.estado = 'puerta'
            self.enviar(PUERTA)

    def enviar(self, destino):
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x, goal.pose.pose.position.y = destino[:2]
        goal.pose.pose.orientation.z = sin(destino[2] / 2)
        goal.pose.pose.orientation.w = cos(destino[2] / 2)
        self.nav.send_goal_async(goal).add_done_callback(self.aceptado)

    def aceptado(self, futuro):
        self.objetivo = futuro.result()
        if not self.objetivo.accepted:
            raise RuntimeError('Nav2 ha rechazado el objetivo')
        self.objetivo.get_result_async().add_done_callback(self.terminado)

    def terminado(self, futuro):
        if futuro.result().status != GoalStatus.STATUS_SUCCEEDED:
            raise RuntimeError('El robot no ha llegado al destino')
        if self.estado == 'puerta':
            self.estado = 'leer'
            self.anterior, self.veces = None, 0
        else:
            self.estado = 'fin'

    def leer(self, mensaje):
        if self.estado != 'leer':
            return
        ids = {dato['id'] for dato in json.loads(mensaje.data) if dato['id'] in DESTINOS}
        actual = ids.pop() if len(ids) == 1 else None
        self.veces = self.veces + 1 if actual is not None and actual == self.anterior else 1
        self.anterior = actual
        if actual is not None and self.veces >= 3:
            self.estado = 'destino'
            self.enviar(DESTINOS[actual])


def main():
    rclpy.init()
    nodo = NavegacionAruco()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        if nodo.objetivo and nodo.estado in ('puerta', 'destino'):
            nodo.objetivo.cancel_goal_async()
    finally:
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

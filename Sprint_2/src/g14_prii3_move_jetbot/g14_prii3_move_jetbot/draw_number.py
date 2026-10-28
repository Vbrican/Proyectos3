#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger


class DrawNumber(Node):

    def __init__(self):
        super().__init__('draw_number')

        # Publicador: envia ordenes de movimiento al robot.
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        # Suscriptor: recibe la posicion y orientacion del robot.
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # Servicios para controlar el dibujo.
        self.stop_service = self.create_service(
            Trigger,
            '/draw_number/stop',
            self.stop_callback
        )

        self.resume_service = self.create_service(
            Trigger,
            '/draw_number/resume',
            self.resume_callback
        )

        self.restart_service = self.create_service(
            Trigger,
            '/draw_number/restart',
            self.restart_callback
        )

        # Trayectoria aproximada del numero 14.
        # "line" indica una distancia en metros.
        # "turn" indica un giro en radianes.
        self.path = [
            ('line', 0.40),              # Dibujar el 1
            ('turn', -math.pi / 2),
            ('line', 0.25),              # Separacion entre digitos
            ('turn', -math.pi / 2),
            ('line', 0.23),              # Primer tramo del 4
            ('turn', 3 * math.pi / 4),
            ('line', 0.32),              # Diagonal del 4
            ('turn', -3 * math.pi / 4),
            ('line', 0.42)               # Ultimo tramo del 4
        ]

        # Posicion y orientacion actuales.
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.have_odom = False

        # Estado del recorrido.
        self.segment_index = 0
        self.segment_initialized = False
        self.paused = False
        self.finished = False

        # Posicion y orientacion al comenzar cada segmento.
        self.start_x = 0.0
        self.start_y = 0.0
        self.start_yaw = 0.0

        # Ejecutar el control a 20 Hz.
        self.timer = self.create_timer(
            0.05,
            self.control_callback
        )

        self.get_logger().info(
            'Nodo draw_number iniciado. Esperando odometria.'
        )

    # --------------------------------------------------
    # 1. RECIBIR LA ODOMETRIA
    # --------------------------------------------------

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        # Convertir la orientacion del cuaternion a yaw.
        sin_yaw = 2.0 * (q.w * q.z + q.x * q.y)
        cos_yaw = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        self.yaw = math.atan2(sin_yaw, cos_yaw)

        self.have_odom = True

    # --------------------------------------------------
    # 2. PUBLICAR UNA ORDEN DE PARADA
    # --------------------------------------------------

    def publish_stop(self):

        msg = Twist()

        msg.linear.x = 0.0
        msg.angular.z = 0.0

        self.publisher.publish(msg)

    # --------------------------------------------------
    # 3. CONTROLAR EL RECORRIDO
    # --------------------------------------------------

    def control_callback(self):

        # No mover el robot sin datos de odometria.
        if not self.have_odom:
            self.publish_stop()
            return

        # Si esta pausado o ha terminado, permanecer parado.
        if self.paused or self.finished:
            self.publish_stop()
            return

        # Comprobar si se han completado todos los segmentos.
        if self.segment_index >= len(self.path):

            self.publish_stop()
            self.finished = True

            self.get_logger().info(
                'Dibujo del numero 14 finalizado.'
            )

            return

        # Guardar la posicion inicial del segmento.
        if not self.segment_initialized:

            self.start_x = self.x
            self.start_y = self.y
            self.start_yaw = self.yaw

            self.segment_initialized = True

            kind, value = self.path[self.segment_index]

            self.get_logger().info(
                f'Segmento {self.segment_index + 1}: '
                f'{kind}, valor={value:.2f}'
            )

        kind, target = self.path[self.segment_index]

        msg = Twist()

        # ----------------------------------------------
        # MOVIMIENTO EN LINEA RECTA
        # ----------------------------------------------

        if kind == 'line':

            dx = self.x - self.start_x
            dy = self.y - self.start_y

            # Distancia recorrida en la direccion inicial.
            progress = (
                dx * math.cos(self.start_yaw)
                + dy * math.sin(self.start_yaw)
            )

            remaining = target - progress

            # Considerar terminado el segmento al acercarse
            # suficientemente al objetivo.
            if abs(remaining) < 0.015:

                self.publish_stop()

                self.segment_index += 1
                self.segment_initialized = False

                return

            # Control proporcional de velocidad.
            msg.linear.x = self.bounded_speed(
                0.8 * remaining,
                maximum=0.10,
                minimum=0.035
            )

        # ----------------------------------------------
        # GIRO SOBRE SI MISMO
        # ----------------------------------------------

        elif kind == 'turn':

            # Diferencia de orientacion desde el comienzo.
            progress = self.normalize_angle(
                self.yaw - self.start_yaw
            )

            remaining = self.normalize_angle(
                target - progress
            )

            if abs(remaining) < 0.04:

                self.publish_stop()

                self.segment_index += 1
                self.segment_initialized = False

                return

            msg.angular.z = self.bounded_speed(
                1.2 * remaining,
                maximum=0.40,
                minimum=0.10
            )

        self.publisher.publish(msg)

    # --------------------------------------------------
    # 4. SERVICIO PARA DETENER EL DIBUJO
    # --------------------------------------------------

    def stop_callback(self, request, response):

        self.paused = True
        self.publish_stop()

        response.success = True
        response.message = 'Dibujo detenido temporalmente.'

        self.get_logger().info(response.message)

        return response

    # --------------------------------------------------
    # 5. SERVICIO PARA REANUDAR EL DIBUJO
    # --------------------------------------------------

    def resume_callback(self, request, response):

        if self.finished:

            response.success = False
            response.message = (
                'El dibujo ha terminado. '
                'Utiliza el servicio restart.'
            )

            return response

        self.paused = False

        response.success = True
        response.message = 'Dibujo reanudado.'

        self.get_logger().info(response.message)

        return response

    # --------------------------------------------------
    # 6. SERVICIO PARA REINICIAR EL DIBUJO
    # --------------------------------------------------

    def restart_callback(self, request, response):

        # Reiniciar la secuencia desde la posicion actual.
        self.segment_index = 0
        self.segment_initialized = False

        self.paused = False
        self.finished = False

        self.publish_stop()

        response.success = True
        response.message = (
            'Recorrido reiniciado desde la posicion actual.'
        )

        self.get_logger().info(response.message)

        return response

    # --------------------------------------------------
    # 7. FUNCIONES AUXILIARES
    # --------------------------------------------------

    @staticmethod
    def normalize_angle(angle):

        return math.atan2(
            math.sin(angle),
            math.cos(angle)
        )

    @staticmethod
    def bounded_speed(value, maximum, minimum):

        if abs(value) < minimum:
            return math.copysign(minimum, value)

        return math.copysign(
            min(abs(value), maximum),
            value
        )


def main(args=None):

    rclpy.init(args=args)

    node = DrawNumber()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

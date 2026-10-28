#!/usr/bin/env python3
"""Dibuja el 14 con TurtleBot3 y permite detener/reanudar/reiniciar."""
import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist
from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker
from std_msgs.msg import Bool  # True = obstaculo, False = camino libre


class DrawNumber(Node):
    # (x_inicial, y_inicial, x_final, y_final), como en Sprint 1.
    TRAMOS = [
        (3.0, 8.2, 3.0, 2.8),
        (8.0, 8.2, 5.5, 5.2),
        (5.5, 5.2, 8.8, 5.2),
        (8.0, 8.2, 8.0, 2.8),
    ]

    def __init__(self):
        super().__init__('draw_number')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.marker_pub = self.create_publisher(Marker, '/draw_number/trazo', 10)
        self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.create_subscription(Bool, '/obstaculo_detectado', self.recibir_obstaculo, 10)
        # El launch decide si es obligatorio recibir datos del LiDAR.
        self.declare_parameter('usar_lidar', False)
        self.usar_lidar = self.get_parameter('usar_lidar').value
        for nombre, callback in (
            ('detener', self.detener),
            ('reanudar', self.reanudar),
            ('reiniciar', self.reiniciar),
        ):
            self.create_service(Trigger, f'/draw_number/{nombre}', callback)

        self.pose = None            # (x, y, yaw)
        self.origen = None          # origen y orientacion del dibujo
        self.ultima_odom = 0.0
        self.segmento = 0
        self.fase = 'ir_inicio'     # ir al trazo o dibujarlo
        self.pausado = True        # no arranca hasta llamar a reanudar
        self.finalizado = False
        self.puntos = []           # pares de puntos para RViz
        self.ultimo_punto = None
        self.obstaculo = None
        self.ultima_senal = 0.0
        self.estado_lidar_anterior = None
        self.create_timer(0.1, self.control)
        self.get_logger().info('Preparado y pausado: llama a /draw_number/reanudar')

    def odom_callback(self, msg):
        pos, q = msg.pose.pose.position, msg.pose.pose.orientation
        yaw = math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2 * (q.y*q.y + q.z*q.z))
        self.pose = (pos.x, pos.y, yaw)
        self.ultima_odom = time.monotonic()
        if self.origen is None:
            self.origen = self.pose

    def recibir_obstaculo(self, msg):
        # El detector de nuestro companero publica el estado por este topic.
        self.obstaculo = msg.data
        self.ultima_senal = time.monotonic()

    @staticmethod
    def normalizar(angulo):
        return math.atan2(math.sin(angulo), math.cos(angulo))

    def convertir(self, x, y):
        ox, oy, a = self.origen
        dx, dy = (x - 3.0) * 0.25, (y - 8.2) * 0.25
        return ox + dx*math.cos(a) - dy*math.sin(a), oy + dx*math.sin(a) + dy*math.cos(a)

    def parar(self):
        self.pub.publish(Twist())

    def marcador(self, borrar=False):
        msg = Marker()
        msg.header.frame_id = 'odom'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.ns, msg.id = 'numero_14', 0
        msg.type = Marker.LINE_LIST
        msg.action = Marker.DELETE if borrar else Marker.ADD
        msg.pose.orientation.w = 1.0
        msg.scale.x = 0.025
        msg.color.g, msg.color.b, msg.color.a = 0.8, 1.0, 1.0
        msg.points = self.puntos
        self.marker_pub.publish(msg)

    def registrar_trazo(self):
        x, y, _ = self.pose
        if self.ultimo_punto is not None:
            ax, ay = self.ultimo_punto
            if math.hypot(x - ax, y - ay) >= 0.015:
                p1, p2 = Point(), Point()
                p1.x, p1.y = ax, ay
                p2.x, p2.y = x, y
                self.puntos.extend([p1, p2])
                self.ultimo_punto = (x, y)
        else:
            self.ultimo_punto = (x, y)

    def control(self):
        if self.pose is None or time.monotonic() - self.ultima_odom > 1.0:
            if not self.pausado:
                self.get_logger().error('Odometria perdida: dibujo pausado')
            self.pausado = True
            self.parar()
            return

        if self.pausado or self.finalizado:
            self.parar()
            self.marcador()
            return

        if self.segmento == len(self.TRAMOS):
            self.finalizado = True
            self.parar()
            self.marcador()
            self.get_logger().info('Numero 14 completado')
            return

        # El modo LiDAR para el robot si hay obstaculo o faltan datos.
        # NO cambia el segmento ni la pausa manual: despues continua solo.
        if self.usar_lidar:
            if self.obstaculo is None or time.monotonic() - self.ultima_senal > 1.0:
                estado = 'sin_datos'
            else:
                estado = 'obstaculo' if self.obstaculo else 'libre'
            if estado != self.estado_lidar_anterior:
                self.get_logger().info(f'Estado LiDAR: {estado}')
                self.estado_lidar_anterior = estado
            if estado != 'libre':
                self.parar()
                self.marcador()
                return

        x1, y1, x2, y2 = self.TRAMOS[self.segmento]
        x_obj, y_obj = self.convertir(*( (x1, y1) if self.fase == 'ir_inicio' else (x2, y2) ))
        if self.fase == 'dibujar':
            self.registrar_trazo()
        self.marcador()

        x, y, yaw = self.pose
        dx, dy = x_obj - x, y_obj - y
        distancia = math.hypot(dx, dy)
        if distancia < 0.04:
            self.parar()
            if self.fase == 'ir_inicio':
                self.fase = 'dibujar'
                self.get_logger().info(f'Dibujando segmento {self.segmento + 1}')
            else:
                self.segmento += 1
                self.fase = 'ir_inicio'
            self.ultimo_punto = None
            return

        error = self.normalizar(math.atan2(dy, dx) - yaw)
        msg = Twist()
        msg.angular.z = max(-0.65, min(0.65, 1.8 * error))
        if abs(error) <= 0.18:
            msg.linear.x = min(0.12, max(0.035, 0.5 * distancia))
        self.pub.publish(msg)

    def detener(self, request, response):
        self.pausado = True
        self.parar()
        response.success, response.message = True, 'Dibujo detenido'
        return response

    def reanudar(self, request, response):
        if self.pose is None or time.monotonic() - self.ultima_odom > 1.0:
            response.success, response.message = False, 'Esperando odometria'
        elif self.finalizado:
            response.success, response.message = False, 'Reinicia primero el dibujo'
        else:
            self.pausado = False
            response.success, response.message = True, 'Dibujo reanudado'
        return response

    def reiniciar(self, request, response):
        self.parar()
        self.segmento, self.fase = 0, 'ir_inicio'
        self.pausado, self.finalizado = True, False
        if self.pose is not None:
            self.origen = self.pose  # no teletransporta al robot
        self.puntos, self.ultimo_punto = [], None
        self.marcador(borrar=True)
        response.success, response.message = True, 'Reiniciado y pausado'
        return response


def main(args=None):
    rclpy.init(args=args)
    nodo = DrawNumber()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.parar()
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


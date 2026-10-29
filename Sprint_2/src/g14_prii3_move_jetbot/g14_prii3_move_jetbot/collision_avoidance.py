# Detector de obstaculos mediante LiDAR

import math
import rclpy

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool


class DetectorColisiones(Node):

    def __init__(self):
        super().__init__('detector_colisiones')

        # Publicador de la señal de obstaculos
        self.pub = self.create_publisher(
            Bool,
            '/obstaculo_detectado',
            10
        )

        # Suscriptor del LiDAR
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.leer_lidar,
            qos_profile_sensor_data
        )

        # Distancia a la que queremos detener el robot
        self.distancia_seguridad = 0.65

        self.get_logger().info(
            'Detector de obstaculos iniciado'
        )

    # Leer las mediciones del LiDAR
    def leer_lidar(self, msg):

        distancias = []
        lecturas_validas = 0

        for i, distancia in enumerate(msg.ranges):

            # Calcular el angulo
            angulo = msg.angle_min + i * msg.angle_increment

            # Normalizar el angulo
            angulo = math.atan2(
                math.sin(angulo),
                math.cos(angulo)
            )

            # Comprobar la zona frontal del robot
            if abs(angulo) <= math.radians(20):

                # Un valor infinito positivo significa
                # que no se detecta objeto en ese rayo
                if math.isinf(distancia) and distancia > 0:
                    lecturas_validas += 1

                elif (
                    math.isfinite(distancia)
                    and msg.range_min <= distancia <= msg.range_max
                ):

                    distancias.append(distancia)
                    lecturas_validas += 1

        # Distancia al obstaculo mas cercano
        distancia_minima = min(
            distancias,
            default=float('inf')
        )

        # Si el LiDAR no proporciona lecturas validas,
        # detenemos el robot por seguridad
        if lecturas_validas == 0:
            detectado = True

        else:
            detectado = (
                distancia_minima < self.distancia_seguridad
            )

        # Enviar la señal al nodo de movimiento
        senal = Bool()
        senal.data = detectado

        self.pub.publish(senal)


def main(args=None):

    rclpy.init(args=args)

    nodo = DetectorColisiones()

    try:
        rclpy.spin(nodo)

    except KeyboardInterrupt:
        pass

    finally:
        nodo.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
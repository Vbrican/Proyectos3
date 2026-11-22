import json
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String


class DetectorAruco(Node):
    def __init__(self):
        super().__init__('detector_aruco_g14')
        self.declare_parameter('diccionario', '5X5_100')
        tipo = self.get_parameter('diccionario').value
        dic = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, 'DICT_' + tipo))

        if hasattr(cv2.aruco, 'ArucoDetector'):
            self.detector = cv2.aruco.ArucoDetector(dic, cv2.aruco.DetectorParameters())
            self.buscar = self.detector.detectMarkers
        else:
            self.buscar = lambda imagen: cv2.aruco.detectMarkers(imagen, dic)

        self.publicador = self.create_publisher(String, '/aruco_detectados', 10)
        self.suscriptor = self.create_subscription(
            Image, '/camera/image_raw', self.leer, qos_profile_sensor_data)

    def leer(self, mensaje):
        formato = mensaje.encoding.lower()
        canales = 4 if formato in ('rgba8', 'bgra8') else 1 if formato == 'mono8' else 3
        imagen = np.frombuffer(mensaje.data, np.uint8).reshape(mensaje.height, mensaje.step)
        imagen = imagen[:, :mensaje.width * canales].reshape(
            mensaje.height, mensaje.width, canales).copy()
        if formato == 'rgb8':
            imagen = cv2.cvtColor(imagen, cv2.COLOR_RGB2BGR)
        elif formato == 'rgba8':
            imagen = cv2.cvtColor(imagen, cv2.COLOR_RGBA2BGR)
        elif formato == 'bgra8':
            imagen = cv2.cvtColor(imagen, cv2.COLOR_BGRA2BGR)
        elif formato == 'mono8':
            imagen = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)

        esquinas, ids, _ = self.buscar(imagen)
        detectados = []
        if ids is not None:
            for identificador, esquina in zip(ids.flatten(), esquinas):
                x, y = np.mean(esquina.reshape(4, 2), axis=0)
                detectados.append({'id': int(identificador), 'x': int(x), 'y': int(y)})
            cv2.aruco.drawDetectedMarkers(imagen, esquinas, ids)

        self.publicador.publish(String(data=json.dumps(detectados)))
        cv2.imshow('ArUcos - Grupo 14', imagen)
        cv2.waitKey(1)


def main():
    rclpy.init()
    nodo = DetectorAruco()
    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

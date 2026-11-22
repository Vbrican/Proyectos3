from setuptools import setup
from glob import glob
import os

nombre = 'g14_prii3_aruco'
setup(
    name=nombre,
    version='0.0.1',
    packages=[nombre],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + nombre]),
        ('share/' + nombre, ['package.xml']),
        (os.path.join('share', nombre, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='grupo14',
    maintainer_email='grupo14@example.invalid',
    description='Deteccion de ArUcos y navegacion automatica en Gazebo',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'detectar_aruco_ros = g14_prii3_aruco.nodo_aruco:main',
        'autonomous_navigation = g14_prii3_aruco.autonomous_navigation:main',
    ]},
)

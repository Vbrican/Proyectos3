from setuptools import find_packages, setup
from glob import glob

package_name = 'g14_prii3_move_turtlebot'

setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(exclude=['test']),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            'share/' + package_name + '/launch',
            glob('launch/*.launch.py')
        ),
    ],

    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='alex',
    maintainer_email='alex@todo.todo',

    description='Movimiento autonomo del numero 14 con TurtleBot3',

    license='MIT',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'draw_number = g14_prii3_move_turtlebot.draw_number:main',
            'collision_avoidance = g14_prii3_move_turtlebot.collision_avoidance:main',
        ],
    },
)

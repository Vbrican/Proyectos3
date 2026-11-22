# Proyecto RII 3 - Sprint 3 - Grupo 14

Este apartado contiene el trabajo realizado para el Sprint 3 de la asignatura **Proyecto RII 3: Robots Inteligentes**.

El objetivo de este sprint es conseguir que el robot TurtleBot3 pueda desplazarse por el laboratorio F1L3 utilizando ROS 2, Gazebo y Nav2.

Se han realizado las siguientes actividades:

- Creación de un mapa del laboratorio mediante SLAM.
- Navegación guiada desde RViz.
- Navegación automática hasta un destino predefinido.
- Detección de códigos ArUco mediante OpenCV.
- Navegación autónoma hacia diferentes destinos dependiendo del ArUco detectado.

El proyecto se ha desarrollado y probado en simulación utilizando el robot **TurtleBot3 Burger**.

---

# 1. Sistema operativo y herramientas utilizadas

Para realizar el proyecto hemos utilizado:

```text
Ubuntu
ROS 2 Humble
Python 3
Gazebo
RViz2
Nav2
OpenCV
TurtleBot3 Burger
```

También utilizamos el paquete `f1l3_gazebo`, que contiene el entorno de simulación del laboratorio.

Para realizar la detección de ArUcos es necesario disponer de OpenCV con el módulo `aruco`.

---

# 2. Archivos del proyecto

El paquete principal de este sprint se llama:

```text
g14_prii3_aruco
```

Su estructura es la siguiente:

```text
g14_prii3_aruco/
│
├── g14_prii3_aruco/
│   ├── __init__.py
│   ├── autonomous_navigation.py
│   └── nodo_aruco.py
│
├── launch/
│   ├── aruco_cenital.launch.py
│   └── aruco_navegacion.launch.py
│
├── resource/
├── map_f1l3.pgm
├── map_f1l3.yaml
├── predefined_navigation.py
├── package.xml
├── setup.py
└── setup.cfg
```

Los archivos principales son:

**`predefined_navigation.py`**

Permite que el robot navegue automáticamente hasta unas coordenadas establecidas previamente.

**`nodo_aruco.py`**

Recibe las imágenes de la cámara del robot, detecta los códigos ArUco y publica sus identificadores.

**`autonomous_navigation.py`**

Controla la navegación autónoma. Primero lleva al robot hasta un punto de lectura y después selecciona el destino dependiendo del ArUco detectado.

**`aruco_navegacion.launch.py`**

Inicia los dos nodos necesarios para realizar la navegación autónoma con ArUcos.

**`map_f1l3.yaml` y `map_f1l3.pgm`**

Contienen el mapa utilizado por Nav2 para desplazarse por el laboratorio.

---

# 3. Descargar el proyecto

Abrimos una terminal y creamos el espacio de trabajo:

```bash
mkdir -p ~/f1l3_ws/src
```

Entramos en la carpeta:

```bash
cd ~/f1l3_ws/src
```

Descargamos el repositorio de GitHub:

```bash
git clone https://github.com/Vbrican/Proyectos3.git
```

Además del repositorio, necesitamos tener instalado el entorno `f1l3_gazebo` proporcionado para la práctica, con los modelos del laboratorio y sus marcadores ArUco.

Este entorno debe estar disponible como paquete ROS 2 en el espacio de trabajo.

---

# 4. Compilar el proyecto

Activamos ROS 2:

```bash
source /opt/ros/humble/setup.bash
```

Entramos en el espacio de trabajo:

```bash
cd ~/f1l3_ws
```

Compilamos:

```bash
colcon build --symlink-install
```

Una vez terminada la compilación, ejecutamos:

```bash
source ~/f1l3_ws/install/setup.bash
```

---

# 5. Configuración inicial

Antes de ejecutar la simulación debemos configurar ROS 2 y seleccionar el modelo del robot.

En las terminales que utilicemos ejecutamos:

```bash
source /opt/ros/humble/setup.bash
source ~/f1l3_ws/install/setup.bash

export ROS_DOMAIN_ID=114
export ROS_LOCALHOST_ONLY=1
export TURTLEBOT3_MODEL=burger
```

Estas variables permiten configurar la comunicación de ROS 2 y seleccionar el TurtleBot3 Burger.

---

# 6. Mapa del laboratorio F1L3

Para realizar la navegación se ha utilizado un mapa generado mediante SLAM.

Los archivos del mapa son:

```text
map_f1l3.yaml
map_f1l3.pgm
```

El archivo `.pgm` contiene la imagen del mapa.

El archivo `.yaml` contiene información como la resolución, el origen y el nombre de la imagen.

Para utilizar los comandos de esta práctica, colocamos ambos archivos en la carpeta personal de Ubuntu.

Si hemos descargado el repositorio siguiendo el apartado 3, podemos copiarlos con:

```bash
cp ~/f1l3_ws/src/Proyectos3/g14_prii3_aruco/map_f1l3.yaml ~/
cp ~/f1l3_ws/src/Proyectos3/g14_prii3_aruco/map_f1l3.pgm ~/
```

Es importante comprobar que el archivo `.yaml` hace referencia a la imagen `map_f1l3.pgm`.

---

# 7. Iniciar la simulación en Gazebo

Abrimos una terminal y ejecutamos:

```bash
source /opt/ros/humble/setup.bash
source ~/f1l3_ws/install/setup.bash

export ROS_DOMAIN_ID=114
export ROS_LOCALHOST_ONLY=1
export TURTLEBOT3_MODEL=burger
```

Después iniciamos Gazebo:

```bash
ros2 launch f1l3_gazebo f1l3_world.launch.py
```

Se abrirá el laboratorio F1L3 con el robot TurtleBot3.

Es necesario mantener esta terminal abierta durante la simulación.

---

# 8. Iniciar Nav2 y cargar el mapa

Abrimos una segunda terminal.

Configuramos ROS 2:

```bash
source /opt/ros/humble/setup.bash
source ~/f1l3_ws/install/setup.bash

export ROS_DOMAIN_ID=114
export ROS_LOCALHOST_ONLY=1
export TURTLEBOT3_MODEL=burger
```

Iniciamos Nav2:

```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True autostart:=True map:=$HOME/map_f1l3.yaml
```

Este comando inicia el sistema de navegación y abre RViz.

Cuando se abra RViz debemos indicar la posición inicial del robot utilizando la herramienta **2D Pose Estimate**.

También debemos comprobar que el robot aparece correctamente situado sobre el mapa.

---

# 9. PBI 3.2 - Navegación guiada

En este apartado se demuestra que el robot puede navegar por el laboratorio utilizando RViz.

Una vez iniciados Gazebo y Nav2:

1. Abrimos RViz.
2. Indicamos la posición inicial con `2D Pose Estimate`.
3. Seleccionamos la herramienta `2D Nav Goal`.
4. Marcamos un punto del laboratorio.
5. El robot calcula una trayectoria y comienza a desplazarse hacia ese destino.

Nav2 se encarga de planificar el recorrido utilizando el mapa y la información de los sensores.

Durante las pruebas comprobamos que el robot podía desplazarse por los pasillos y alcanzar los puntos seleccionados.

---

# 10. PBI 3.3 - Navegación predefinida

En este apartado hemos creado un programa que permite que el robot vaya automáticamente hasta un destino establecido previamente.

El archivo utilizado es:

```text
predefined_navigation.py
```

El programa utiliza un cliente de acción ROS 2 para enviar un objetivo a Nav2 mediante:

```text
/navigate_to_pose
```

## 10.1 Coordenadas del destino

Hemos seleccionado el siguiente punto del laboratorio:

```text
X = -1.194
Y = 7.200
Yaw = 0.9495
```

Estas coordenadas corresponden al destino 1 de nuestra simulación.

## 10.2 Ejecutar la navegación predefinida

Primero debemos tener abiertos Gazebo y Nav2, siguiendo los apartados 7 y 8.

Después abrimos una tercera terminal.

Ejecutamos:

```bash
source /opt/ros/humble/setup.bash

export ROS_DOMAIN_ID=114
export ROS_LOCALHOST_ONLY=1
```

Iniciamos el programa:

```bash
python3 ~/f1l3_ws/src/Proyectos3/g14_prii3_aruco/predefined_navigation.py --ros-args -p use_sim_time:=true
```

El robot comenzará a navegar automáticamente hacia el destino establecido.

No es necesario indicar manualmente el objetivo en RViz.

Cuando el robot llega correctamente aparece:

```text
Destino alcanzado
```

## 10.3 Resultado

Se ha comprobado que el robot realiza el recorrido de forma automática y llega a las coordenadas establecidas.

---

# 11. PBI 3.4 - Navegación autónoma con ArUcos

En este apartado hemos implementado un sistema que permite seleccionar automáticamente el destino del robot mediante códigos ArUco.

El funcionamiento se divide en dos programas.

**Detector de ArUcos**

Archivo:

```text
nodo_aruco.py
```

Este nodo recibe las imágenes de la cámara desde el topic:

```text
/camera/image_raw
```

Utiliza OpenCV para detectar los marcadores y publica los identificadores encontrados en:

```text
/aruco_detectados
```

**Navegación autónoma**

Archivo:

```text
autonomous_navigation.py
```

Este nodo recibe los identificadores publicados por el detector y envía los objetivos correspondientes a Nav2.

## 11.1 Funcionamiento

La navegación se realiza siguiendo esta secuencia:

1. El robot comienza en su posición inicial.
2. Navega automáticamente hasta el punto de lectura.
3. Utiliza la cámara para detectar un código ArUco.
4. Comprueba el identificador del marcador.
5. Selecciona el destino correspondiente.
6. Envía las coordenadas a Nav2.
7. Navega automáticamente hasta el destino final.

El robot utiliza la misma acción `/navigate_to_pose` que en el apartado anterior.

## 11.2 Punto de lectura

El robot se desplaza inicialmente hasta:

```text
X = 3.263
Y = 1.687
Yaw = 2.0
```

En este punto se realiza la lectura del código ArUco.

## 11.3 Identificadores utilizados

Para la simulación hemos utilizado tres códigos ArUco diferentes:

| ArUco | Destino | X | Y | Yaw |
|---|---|---|---|---|
| ID 5 | Destino 1 | -1.194 | 7.200 | 0.9495 |
| ID 17 | Destino 2 | 3.729 | 14.077 | -1.5425 |
| ID 6 | Destino 3 | 3.796 | 11.707 | -1.5425 |

El detector utiliza el diccionario:

```text
DICT_5X5_100
```

Cada identificador está relacionado con un destino diferente.

Para evitar lecturas puntuales incorrectas, el programa confirma el mismo identificador en tres detecciones consecutivas antes de seleccionar el destino.

---

# 12. Ejecutar la navegación autónoma

Primero debemos tener abiertos:

- Gazebo con el laboratorio F1L3.
- Nav2 con el mapa.
- RViz con la posición inicial correctamente indicada.

Después abrimos una tercera terminal y ejecutamos:

```bash
source /opt/ros/humble/setup.bash
source ~/f1l3_ws/install/setup.bash

export ROS_DOMAIN_ID=114
export ROS_LOCALHOST_ONLY=1
```

Iniciamos los nodos:

```bash
ros2 launch g14_prii3_aruco aruco_navegacion.launch.py
```

Este archivo inicia automáticamente el detector de ArUcos y el programa de navegación autónoma.

El robot comienza desplazándose hasta el punto de lectura.

Cuando detecta un código ArUco válido, selecciona su destino y navega hasta él.

---

# 13. Comprobación del funcionamiento

Para comprobar el sistema realizamos tres pruebas utilizando los diferentes marcadores.

## 13.1 Primera prueba - ArUco ID 5

Colocamos el marcador ID 5 en la posición de lectura.

El robot detecta el identificador y navega hasta el destino 1.

```text
X = -1.194
Y = 7.200
```

**Resultado: recorrido completado correctamente.**

## 13.2 Segunda prueba - ArUco ID 17

Colocamos el marcador ID 17.

El robot detecta el identificador y navega hasta el destino 2.

```text
X = 3.729
Y = 14.077
```

**Resultado: recorrido completado correctamente.**

## 13.3 Tercera prueba - ArUco ID 6

Colocamos el marcador ID 6.

El robot detecta el identificador y navega hasta el destino 3.

```text
X = 3.796
Y = 11.707
```

**Resultado: recorrido completado correctamente.**

Se han realizado demostraciones de los tres recorridos.

---

# 14. Topics y acciones utilizados

Durante el proyecto utilizamos los siguientes elementos de ROS 2:

| Nombre | Tipo | Función |
|---|---|---|
| `/camera/image_raw` | Topic | Recibir imágenes de la cámara. |
| `/aruco_detectados` | Topic | Publicar los ArUcos detectados. |
| `/navigate_to_pose` | Acción | Enviar objetivos de navegación a Nav2. |
| `/scan` | Topic | Recibir las medidas del LiDAR. |
| `/map` | Topic | Obtener el mapa del entorno. |

Los dos programas principales se comunican mediante el topic `/aruco_detectados`.

El detector publica los identificadores y el programa de navegación utiliza esa información para seleccionar el destino.

---

# 15. Resultados obtenidos

Durante el Sprint 3 hemos conseguido:

- Generar un mapa del laboratorio mediante SLAM.
- Navegar por el entorno utilizando RViz.
- Realizar una navegación predefinida hasta un punto establecido.
- Detectar códigos ArUco utilizando la cámara del robot y OpenCV.
- Seleccionar diferentes destinos según el identificador detectado.
- Completar automáticamente los tres recorridos en simulación.

El sistema se ha probado satisfactoriamente en Gazebo.

La navegación autónoma se ha comprobado utilizando los identificadores 5, 17 y 6.

---

# 16. Observaciones

Para reproducir la simulación es necesario disponer del mundo `f1l3_gazebo`, los modelos ArUco utilizados y el mapa del laboratorio.

La navegación guiada, la navegación predefinida y la navegación autónoma se han probado utilizando los lanzamientos indicados en este documento.

El lanzamiento que reúne todos los componentes en un único archivo está pendiente de validación, por lo que se documenta el procedimiento de ejecución probado.

---

# 17. Conclusión

En este sprint hemos conseguido implementar diferentes formas de navegación para el robot TurtleBot3 dentro del laboratorio F1L3.

Primero utilizamos Nav2 para realizar recorridos guiados desde RViz.

Después desarrollamos un programa de navegación predefinida que permite enviar al robot a un destino establecido automáticamente.

Finalmente, implementamos la detección de códigos ArUco y la navegación autónoma, consiguiendo que el robot seleccione entre tres destinos diferentes dependiendo del marcador detectado.

Las pruebas realizadas en Gazebo han permitido comprobar el funcionamiento de los recorridos implementados.

**Proyecto RII 3 - Sprint 3 - Grupo 14**

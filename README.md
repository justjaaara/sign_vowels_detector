# Proyecto de Reconocimiento de Lengua de Señas para Vocales

![Lengua de señas Colombiana](https://i.gyazo.com/608adcf42f681fce3a238f3b1fadc71d.png)

## Descripción General

Este proyecto implementa un sistema de reconocimiento de lengua de señas en tiempo real para vocales (A, E, I, O, U) utilizando visión por computadora y aprendizaje profundo. El sistema detecta las manos del usuario a través de la cámara web, reconoce la seña realizada y la clasifica según la vocal correspondiente.

## Tecnologías Utilizadas

- **Python 3.12**: Lenguaje de programación principal
- **OpenCV**: Biblioteca para procesamiento de imágenes y visión por computadora
- **MediaPipe**: Framework para la detección de manos y puntos de referencia
- **YOLOv8**: Modelo de inteligencia artificial para clasificación de señas
- **Ultralytics**: API para entrenar y ejecutar modelos YOLO
- **Threading**: Para procesamiento asíncrono que mejora el rendimiento

## Estructura del Proyecto

```
/Vocales
├── data/                      # Imágenes de entrenamiento organizadas por vocales
│   ├── Letra_A/               # Imágenes para la vocal A
│   ├── Letra_E/               # Imágenes para la vocal E
│   ├── Letra_I/               # Imágenes para la vocal I
│   ├── Letra_O/               # Imágenes para la vocal O
│   └── Letra_U/               # Imágenes para la vocal U
├── dataset/                   # Datos preparados para entrenamiento y validación
│   ├── train/                 # Conjunto de entrenamiento
│   └── val/                   # Conjunto de validación
├── runs/                      # Resultados de entrenamiento y modelos generados
│   ├── detect/                # Modelos de detección
│   └── segment/               # Modelos de segmentación
├── dataset.yaml               # Configuración del conjunto de datos para YOLO
├── Data.py                    # Script para capturar imágenes de entrenamiento
├── Inferencia.py              # Versión inicial del script de inferencia
├── Inferencia_optimizado.py   # Versión optimizada del script de inferencia
├── SeguimientoManos.py        # Clase para detección y seguimiento de manos
└── README.md                  # Este documento
```

## Componentes Principales

### 1. Módulo de Detección de Manos (`SeguimientoManos.py`)

Este módulo implementa la clase `detectormanos` que utiliza MediaPipe para detectar y rastrear manos en tiempo real. Proporciona funcionalidades como:

- Detección de manos en una imagen
- Extracción de puntos clave (landmarks) de las manos
- Determinación de qué dedos están levantados
- Cálculo de distancias entre puntos específicos

### 2. Captura de Datos (`Data.py`)

Script utilizado para capturar imágenes de entrenamiento. Detecta manos, las recorta y guarda las imágenes en carpetas específicas para cada vocal.

### 3. Motor de Inferencia (`Inferencia_optimizado.py`)

El componente principal que realiza la detección y clasificación de señas en tiempo real. Utiliza técnicas de optimización como:

- Procesamiento asíncrono en hilos separados
- Submuestreo de frames (procesamiento de 1 de cada N frames)
- Redimensionamiento de imágenes para acelerar la inferencia
- Memoria caché de resultados para mantener la fluidez

### 4. Modelo YOLOv8

El sistema utiliza un modelo YOLOv8 entrenado para detectar y clasificar las señas de vocales. El modelo fue entrenado con imágenes capturadas específicamente para este proyecto.

## Instalación y Requisitos

### Requisitos de Hardware

- Cámara web
- CPU: Intel Core i5 o superior (recomendado)
- RAM: 8GB o superior
- GPU: Opcional, mejora el rendimiento

### Requisitos de Software

- Python 3.10 o superior
- Pip (administrador de paquetes de Python)

### Dependencias

Instala las dependencias necesarias con:

```bash
pip install -r requirements.txt
```

## Ejecución del Proyecto

### Ejecución de la Aplicación Principal

1. Abre una terminal
2. Navega al directorio del proyecto:
   ```bash
   cd /home/felipe/Desktop/Vocales
   ```
3. Ejecuta el script de inferencia optimizado:
   ```bash
   python Inferencia_optimizado.py
   ```

### Controles

- **ESC**: Cerrar la aplicación
- La aplicación muestra la clasificación de la seña en tiempo real cuando detecta una mano

## Funcionamiento

1. **Detección de Manos**: El sistema utiliza MediaPipe para detectar manos en el video de la cámara.
2. **Extracción de ROI**: Cuando se detecta una mano, se extrae la región de interés (ROI).
3. **Inferencia Asíncrona**: La ROI se procesa en un hilo separado para mantener la fluidez de la interfaz.
4. **Clasificación**: El modelo YOLOv8 clasifica la seña en una de las cinco vocales.
5. **Visualización**: Los resultados se muestran en tiempo real, con la seña detectada y su nivel de confianza.

## Optimizaciones de Rendimiento

- **Procesamiento Selectivo**: Solo se procesan 1 de cada 10 frames para reducir la carga de la CPU.
- **Redimensionamiento Adaptativo**: Las imágenes se redimensionan antes del procesamiento.
- **Procesamiento Asíncrono**: La detección y clasificación ocurren en un hilo separado.
- **Visualización Eficiente**: Se mantiene un único stream de video con superposición de resultados.

## Entrenamiento del Modelo

Para entrenar o continuar el entrenamiento del modelo:

```bash
yolo task=detect mode=train resume=true epochs=30 data=/home/felipe/Desktop/Vocales/dataset.yaml model=/home/felipe/Desktop/Vocales/runs/detect/train/weights/last.pt imgsz=640 batch=2 save_period=10 lr0=0.001
```

Parámetros:
- `task=detect`: Tipo de tarea (detección de objetos)
- `mode=train`: Modo de entrenamiento
- `resume=true`: Continuar desde el último checkpoint
- `epochs=230`: Número total de epochs
- `data=...`: Ruta al archivo de configuración del dataset
- `model=...`: Ruta al modelo base o último checkpoint
- `imgsz=640`: Tamaño de imagen para entrenamiento
- `batch=2`: Tamaño del batch
- `save_period=10`: Guardar checkpoints cada 10 epochs
- `lr0=0.001`: Tasa de aprendizaje inicial

## Limitaciones y Mejoras Futuras

- **Rendimiento en CPU**: La inferencia puede ser lenta en sistemas sin GPU
- **Condiciones de Iluminación**: El sistema puede verse afectado por condiciones de luz deficientes
- **Conjunto de Datos Limitado**: Actualmente solo reconoce vocales, se podría expandir a más señas

## Créditos y Agradecimientos

Este proyecto utiliza tecnologías y bibliotecas de código abierto:
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://mediapipe.dev/)
- [YOLOv8 por Ultralytics](https://github.com/ultralytics/ultralytics)

---

*Este proyecto fue desarrollado como parte de una iniciativa para facilitar la comunicación mediante lengua de señas utilizando tecnologías de visión por computadora y aprendizaje automático.*

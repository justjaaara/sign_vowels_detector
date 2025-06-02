import cv2
import os
import numpy as np
import time
import threading
import serial

# Variables globales para seguimiento de vocales
last_sent_vowel = None
last_sent_time = 0
VOWEL_SEND_DELAY = 1.0  # Tiempo mínimo entre envíos de la misma vocal (segundos)
waiting_for_esp32 = False  # Indica si estamos esperando respuesta del ESP32

# Configurar el puerto serial (ajusta el puerto y la velocidad según tu configuración)
try:
    esp32 = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    esp32.flush()  # Limpiar el buffer
    print("Puerto serial conectado correctamente")
    # Enviar un mensaje inicial al ESP32
    mensaje_inicial = "HOLA\n"
    esp32.write(mensaje_inicial.encode())
    print(f"Mensaje inicial enviado: {mensaje_inicial}")
    
    # Esperar a que el ESP32 esté listo
    waiting_for_esp32 = True
    print("Esperando a que el ESP32 esté listo...")
    while waiting_for_esp32:
        if esp32.in_waiting > 0:
            respuesta = esp32.readline().decode('utf-8').strip()
            print(respuesta)
            print(f"Respuesta del ESP32: {respuesta}")
            if respuesta == "LISTO":
                waiting_for_esp32 = False
                print("ESP32 listo para recibir comandos")
        time.sleep(0.1)
except Exception as e:
    print(f"Error al conectar al puerto serial: {e}")
    exit()

# importar clase seguimiento Mano
import SeguimientoManos as sm
from ultralytics import YOLO

# Configuración para mejorar rendimiento
PROCESS_EVERY_N_FRAMES = 10  # Procesar con YOLO cada N frames
DETECTION_BUFFER_SIZE = 5    # Tamaño del buffer para suavizar detecciones
RESIZE_FACTOR = 0.3          # Factor para reducir el tamaño del frame
MODEL_CONFIDENCE = 0.5       # Umbral de confianza para el modelo

# Variables globales para procesamiento en segundo plano
last_result = None
last_anotaciones = None
processing_lock = threading.Lock()
is_processing = False



# Procesar predicción en segundo plano
def process_hand_async(recorte, model):
    global last_result, last_anotaciones, is_processing
    
    try:
        # Reducir el tamaño para acelerar el procesamiento
        small_recorte = cv2.resize(recorte, (0, 0), fx=RESIZE_FACTOR, fy=RESIZE_FACTOR)
        
        # Ejecutar predicción
        resultados = model.predict(small_recorte, conf=MODEL_CONFIDENCE)
        
        # Guardar resultados
        with processing_lock:
            last_result = resultados
            if len(resultados) > 0:
                last_anotaciones = resultados[0].plot()
            else:
                last_anotaciones = recorte.copy()
            is_processing = False
    except Exception as e:
        print(f"Error en procesamiento asíncrono: {e}")
        with processing_lock:
            is_processing = False

# Verificar si la cámara está disponible
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
    exit()

# Configurar resolución más baja para mejorar FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Leer modelo con optimizaciones
try:
    model = YOLO('/home/felipe/Desktop/Vocales/runs/detect/train/weights/best.pt')
    print("Modelo cargado exitosamente")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()

detector = sm.detectormanos(Confdeteccion=0.7)  # Reducir umbral para mejorar rendimiento

# Variables para el contador de FPS
ptime = 0
frame_counter = 0

# Buffer para las últimas detecciones
last_detections = []

while True:
    # Realizar la lectura de la cap
    ret, frame = cap.read()
    
    if not ret:
        print("Error: No se pudo leer el frame de la cámara")
        break
    
    # Calcular FPS
    ctime = time.time()
    fps = 1 / (ctime - ptime) if ptime > 0 else 0
    ptime = ctime
    
    # Mostrar FPS
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    frame_counter += 1
        
    try:
        # Extraer información de la mano
        frame = detector.encontrarmanos(frame, dibujar=False)
        
        # Posición de una sola mano
        lista1, bbox, mano = detector.encontrarposicion(frame, ManoNum=0, dibujarPuntos=False, dibujarBox=False, color=(0, 255, 0))
        
        # Si hay mano
        if mano == 1:
            # Extraer la información del cuadro
            xmin, ymin, xmax, ymax = bbox
            
            # Asignar margen con verificación de límites
            xmin = max(0, xmin - 40)
            ymin = max(0, ymin - 40)
            xmax = min(frame.shape[1], xmax + 40)
            ymax = min(frame.shape[0], ymax + 40)
            
            # Dibujar rectángulo alrededor de la mano
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), [0, 255, 0], 2)
            
            # Procesar solo cada N frames o si no hay procesamiento en curso
            if (frame_counter % PROCESS_EVERY_N_FRAMES == 0 or last_result is None) and not is_processing:
                if ymin < ymax and xmin < xmax:
                    recorte = frame[ymin:ymax, xmin:xmax]
                    with processing_lock:
                        is_processing = True
                    
                    # Iniciar procesamiento en segundo plano
                    thread = threading.Thread(target=process_hand_async, args=(recorte, model))
                    thread.daemon = True
                    thread.start()
            
            # Mostrar resultados si están disponibles
            with processing_lock:
                if last_anotaciones is not None:
                    # Redimensionar el recorte para la visualización
                    h, w = frame.shape[:2]
                    recorte_height = h // 3
                    recorte_width = int(last_anotaciones.shape[1] * recorte_height / last_anotaciones.shape[0])
                    anotaciones_resized = cv2.resize(last_anotaciones, (recorte_width, recorte_height))
                    
                    # Colocar la imagen recortada en la esquina superior derecha
                    if anotaciones_resized.shape[2] == 3:  # Verificar que sea RGB
                        roi = frame[10:10+recorte_height, w-recorte_width-10:w-10]
                        frame[10:10+recorte_height, w-recorte_width-10:w-10] = anotaciones_resized
                    
                    # Mostrar clase si se detectó algo
                    if last_result is not None and len(last_result) > 0:
                        for r in last_result:
                            for box in r.boxes:
                                cls_id = int(box.cls[0].item())
                                cls_name = r.names[cls_id]
                                conf = box.conf[0].item()
                                
                                # Enviar la vocal detectada al ESP32 solo si ha cambiado o ha pasado suficiente tiempo
                                # y si no estamos esperando una confirmación del ESP32
                                current_time = time.time()
                                if not waiting_for_esp32 and (cls_name != last_sent_vowel or 
                                    (current_time - last_sent_time) > VOWEL_SEND_DELAY):
                                    # Convertir el nombre de la clase al formato esperado por el ESP32
                                    vocal_a_enviar = f"Letra_{cls_name.split('_')[-1]}\n"
                                    try:
                                        esp32.write(vocal_a_enviar.encode())
                                        print(f"Vocal enviada al ESP32: {vocal_a_enviar.strip()}")
                                        # Actualizar variables globales
                                        last_sent_vowel = cls_name
                                        last_sent_time = current_time
                                        waiting_for_esp32 = True  # Ahora esperamos la respuesta
                                    except Exception as e:
                                        print(f"Error al enviar al ESP32: {e}")
                                
                                # Verificar si hay respuesta del ESP32
                                if waiting_for_esp32:
                                    if esp32.in_waiting > 0:
                                        try:
                                            respuesta = esp32.readline().decode('utf-8').strip()
                                            print(f"Respuesta del ESP32: '{respuesta}'")
                                            if "LISTO" in respuesta:
                                                waiting_for_esp32 = False
                                                print("ESP32 listo para la siguiente vocal")
                                        except Exception as e:
                                            print(f"Error al leer respuesta del ESP32: {e}")
                                            # Si hay error, reiniciamos para evitar bloqueo
                                            waiting_for_esp32 = False
                                
                                cv2.putText(frame, f"{cls_name}: {conf:.2f}", (xmin, ymin-10), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
    
    # Mostrar el resultado final en una única ventana
    cv2.imshow("LENGUAJE VOCALES", frame)
    
    # Leer nuestro teclado
    t = cv2.waitKey(1)
    if t == 27:  # Tecla ESC
        break

# Cerrar recursos
cap.release()
cv2.destroyAllWindows()
if 'esp32' in locals():
    esp32.close()
    print("Puerto serial cerrado")

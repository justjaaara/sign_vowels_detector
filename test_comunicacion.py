# Código para PC - Prueba de comunicación con ESP32
import serial
import time

# Configurar el puerto serial (ajusta el puerto según tu configuración)
try:
    # En Linux suele ser /dev/ttyUSB0 o /dev/ttyACM0
    # En Windows suele ser COM3, COM4, etc.
    esp32 = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    time.sleep(2)  # Dar tiempo al ESP32 para inicializarse
    esp32.flush()  # Limpiar el buffer
    print("Puerto serial conectado correctamente")
except Exception as e:
    print(f"Error al conectar al puerto serial: {e}")
    exit()

try:
    # Enviar mensajes de prueba
    for i in range(5):
        mensaje = f"PRUEBA {i+1}\n"
        esp32.write(mensaje.encode())
        print(f"Mensaje enviado: {mensaje.strip()}")
        
        # Esperar respuesta
        time.sleep(0.5)
        if esp32.in_waiting > 0:
            respuesta = esp32.readline().decode('utf-8').strip()
            print(f"Respuesta del ESP32: {respuesta}")
        
        time.sleep(1)
    
    print("Prueba de comunicación completada")
except Exception as e:
    print(f"Error durante la comunicación: {e}")
finally:
    esp32.close()
    print("Puerto serial cerrado")
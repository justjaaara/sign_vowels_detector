import serial
import time

# Cambia '/dev/ttyUSB0' por el puerto correspondiente (verifícalo con `ls /dev/ttyUSB*`)
puerto = '/dev/ttyUSB0'
baudrate = 115200

try:
    with serial.Serial(puerto, baudrate, timeout=1) as ser:
        print(f"Conectado a {puerto}")
        while True:
            mensaje = input("Escribe un mensaje para enviar al ESP32 (o 'salir'): ")
            if mensaje.lower() == "salir":
                print("Cerrando conexión.")
                break
            ser.write((mensaje + '\n').encode('utf-8'))
            print("Mensaje enviado.")
except serial.SerialException as e:
    print(f"Error al abrir el puerto: {e}")

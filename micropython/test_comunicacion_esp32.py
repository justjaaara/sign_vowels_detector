import sys
import select
import time
from machine import I2S, Pin, UART
import os

# Configuración del I2S para el MAX98357A
bck_pin = Pin(26)    # BCLK
ws_pin = Pin(25)     # LRCLK (WS)
sdout_pin = Pin(22)  # SD (DIN)

# Configurar el audio I2S
audio_out = I2S(
    0,                      # Número de periférico I2S
    sck=bck_pin,            # Pin de reloj
    ws=ws_pin,              # Pin de selección de palabra
    sd=sdout_pin,           # Pin de datos
    mode=I2S.TX,            # Modo de transmisión
    bits=16,                # Bits por muestra
    format=I2S.STEREO,      # Formato estéreo
    rate=44100,             # Frecuencia de muestreo
    ibuf=20000              # Tamaño del buffer interno
)

# Configuración del UART para comunicación con el PC
uart = UART(1, baudrate=115200, tx=17, rx=16, timeout=1000)

# Reemplazar las funciones de entrada/salida estándar con UART
def enviar_mensaje(mensaje):
    uart.write(mensaje + '\n')

def recibir_mensaje():
    if uart.any():
        return uart.readline().decode('utf-8').strip()
    return None

def reproducir_audio(letra):
    """Reproduce el archivo de audio correspondiente a la letra."""
    archivo = None
    
    # Mapeo de letras a archivos de audio
    if letra == "Letra_A":
        archivo = "/vocales_audio/a.wav"
    elif letra == "Letra_E":
        archivo = "/vocales_audio/e.wav"
    elif letra == "Letra_I":
        archivo = "/vocales_audio/i.wav"
    elif letra == "Letra_O":
        archivo = "/vocales_audio/o.wav"
    elif letra == "Letra_U":
        archivo = "/vocales_audio/u.wav"
    
    if archivo is None:
        print("Archivo de audio no encontrado para:", letra)
        # Enviar confirmación de que estamos listos para la siguiente letra
        print("LISTO")
        return
    
    try:
        # Abrir el archivo WAV
        f = open(archivo, "rb")
        
        # Saltar el encabezado WAV (44 bytes)
        f.seek(44)
        
        # Leer y reproducir el audio en bloques
        bloque = bytearray(1024)
        while True:
            bytes_leidos = f.readinto(bloque)
            if bytes_leidos == 0:
                break
            # Si no se llenó el bloque completo
            if bytes_leidos < len(bloque):
                # Rellenar el resto con ceros
                for i in range(bytes_leidos, len(bloque)):
                    bloque[i] = 0
            
            # Escribir el bloque en el I2S
            audio_out.write(bloque)
        
        # Esperar a que se termine de reproducir
        audio_out.wait_tx_done()
        f.close()
        print("Audio reproducido:", archivo)
        # Enviar confirmación de que estamos listos para la siguiente letra
        print("LISTO")
    except:
        print("Error al reproducir audio")
        # Incluso en caso de error, enviar confirmación
        print("LISTO")

print("ESP32 listo para recibir datos desde el PC.")
# Enviar señal inicial de que estamos listos para recibir
enviar_mensaje("LISTO")

while True:
    mensaje = recibir_mensaje()
    if mensaje:
        print("Recibido desde el PC:", mensaje)
        
        # Reproducir audio correspondiente a la letra recibida
        if mensaje.startswith("Letra_"):
            reproducir_audio(mensaje)
        
        if mensaje == "salir":
            print("Deteniendo recepción.")
            break
    time.sleep(0.1)

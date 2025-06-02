import sys
import select
import time
from machine import I2S, Pin
import os

# Configuración de pines para el MAX98357A
BCLK_PIN = 26
WS_PIN = 25
DOUT_PIN = 22

# Configuración de I2S para audio
SAMPLE_RATE = 44100  # Frecuencia de muestreo estándar para mejor calidad
BITS_PER_SAMPLE = 16
BUFFER_LENGTH_IN_BYTES = 4096  # Buffer más grande para reproducción más fluida

# Inicializar I2S para reproducción de audio
audio_out = I2S(
    0,                      # Número de periférico I2S (0 o 1)
    sck=Pin(BCLK_PIN),     # Pin de reloj serial (BCLK)
    ws=Pin(WS_PIN),        # Pin de selección de palabra (LRC)
    sd=Pin(DOUT_PIN),      # Pin de datos seriales (DIN)
    mode=I2S.TX,           # Modo de transmisión
    bits=BITS_PER_SAMPLE,  # Bits por muestra
    format=I2S.MONO,       # Cambiado a MONO ya que MAX98357A es un amplificador mono
    rate=SAMPLE_RATE,      # Tasa de muestreo
    ibuf=BUFFER_LENGTH_IN_BYTES  # Tamaño del buffer
)

# Ruta a los archivos de audio
AUDIO_PATH = "vocales_audio"

# Variable global para controlar si se está reproduciendo audio
reproduciendo_audio = False

# Variable global para controlar si se está reproduciendo audio
reproduciendo_audio = False

# Función para reproducir un archivo WAV
def play_wav(file_path):
    global reproduciendo_audio
    try:
        # Marcar que estamos reproduciendo audio
        reproduciendo_audio = True
        
        # Abrir el archivo WAV
        with open(file_path, "rb") as wav_file:
            # Saltar el encabezado WAV (primeros 44 bytes típicamente)
            wav_file.seek(44)  # Saltar encabezado WAV estándar
            
            # Leer y reproducir los datos del archivo en bloques
            chunk_size = 1024
            data = bytearray(chunk_size)
            
            # Para un buffer más estable
            audio_out.write(bytearray(chunk_size))  # Escribir silencio para estabilizar
            
            while True:
                num_read = wav_file.readinto(data)
                if num_read == 0:
                    break
                
                # Asegurarse de que los datos se envían correctamente
                if num_read < chunk_size:
                    # Rellenar con ceros si es necesario
                    for i in range(num_read, chunk_size):
                        data[i] = 0
                    
                # Escribir datos al dispositivo I2S
                audio_out.write(data)
        
        # Agregar un pequeño silencio al final para evitar cortes abruptos
        audio_out.write(bytearray(chunk_size))
        
        # Asegurarse de que todo el audio se ha reproducido
        audio_out.wait_tx_done()
        print(f"Audio {file_path} reproducido correctamente")
        
        # Enviar confirmación al PC
        print("AUDIO_TERMINADO")
        
        # Marcar que ya no estamos reproduciendo audio
        reproduciendo_audio = False
    except Exception as e:
        print(f"Error al reproducir audio {file_path}: {e}")
        # En caso de error, también marcamos que no estamos reproduciendo
        reproduciendo_audio = False

print("ESP32 listo para recibir datos desde el PC.")

while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        mensaje = sys.stdin.readline().strip()
        print("Recibido desde el PC:", mensaje)
        
        # Solo procesar el mensaje si no estamos reproduciendo audio
        if not reproduciendo_audio:
            # Procesar el mensaje para identificar la vocal
            if mensaje == "salir":
                print("Deteniendo recepción.")
                break
            elif mensaje == "Letra_A" or mensaje == "A":
                audio_file = f"{AUDIO_PATH}/a.wav"
                play_wav(audio_file)
            elif mensaje == "Letra_E" or mensaje == "E":
                audio_file = f"{AUDIO_PATH}/e.wav"
                play_wav(audio_file)
            elif mensaje == "Letra_I" or mensaje == "I":
                audio_file = f"{AUDIO_PATH}/i.wav"
                play_wav(audio_file)
            elif mensaje == "Letra_O" or mensaje == "O":
                audio_file = f"{AUDIO_PATH}/o.wav"
                play_wav(audio_file)
            elif mensaje == "Letra_U" or mensaje == "U":
                audio_file = f"{AUDIO_PATH}/u.wav"
                play_wav(audio_file)
        else:
            # Informar que se está reproduciendo audio
            print("Reproduciendo audio, mensaje ignorado")
            
    time.sleep(0.1)

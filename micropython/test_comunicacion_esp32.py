# Código para ejecutar en el ESP32
import machine
import time
from machine import Pin, I2S
import os

# Configuración de UART para comunicación con el PC
# Usamos UART2 (en lugar de UART0) para evitar conflictos con la comunicación USB
# UART2 está en GPIO16 (RX) y GPIO17 (TX) por defecto
uart = machine.UART(2, baudrate=115200)
uart.init(115200, bits=8, parity=None, stop=1, tx=17, rx=16)
print("UART2 inicializado en GPIO16 (RX) y GPIO17 (TX)")

# Configurar I2S para reproducción de audio con MAX98357A
# Usando los pines que has conectado:
# GPIO26 -> BCK (Bit Clock)
# GPIO25 -> LRC/WS (Word Select)
# GPIO22 -> DIN (Data In al amplificador)
bck_pin = Pin(26)  # Bit clock
ws_pin = Pin(25)   # Word select/LRC
sdout_pin = Pin(22)  # Serial data out al MAX98357A

# Configurar I2S optimizado para MAX98357A con valores más conservadores
# Reducimos samplerate y aumentamos buffers para evitar ESP_ERR_INVALID_STATE
try:
    audio_out = I2S(
        I2S.NUM0,
        bck=bck_pin, 
        ws=ws_pin, 
        sdout=sdout_pin,
        standard=I2S.PHILIPS, 
        mode=I2S.MASTER_TX,
        dataformat=I2S.B16, 
        channelformat=I2S.ONLY_RIGHT,
        samplerate=16000,  # Reducido de 22050 a 16000
        dmacount=16,      # Aumentado de 8 a 16
        dmalen=128        # Ajustado a 128
    )
    print("I2S inicializado correctamente")
except OSError as e:
    print(f"Error al inicializar I2S: {e}")
    # Intento con configuración alternativa
    try:
        time.sleep(1)
        audio_out = I2S(
            I2S.NUM0,
            bck=bck_pin, 
            ws=ws_pin, 
            sdout=sdout_pin,
            standard=I2S.PHILIPS, 
            mode=I2S.MASTER_TX,
            dataformat=I2S.B16, 
            channelformat=I2S.MONO,  # Cambiado a MONO en lugar de ONLY_RIGHT
            samplerate=8000,         # Reducido aún más
            dmacount=8,
            dmalen=64
        )
        print("I2S inicializado con configuración alternativa")
    except OSError as e:
        print(f"Error al inicializar I2S (segundo intento): {e}")
        # Seguiremos sin audio, pero al menos podremos comunicarnos

def reproducir_audio(vocal):
    try:
        # Ruta al archivo de audio para cada vocal
        ruta_audio = f"/vocales_audio/{vocal.lower()}.wav"
        
        # Verificar si el audio_out está definido y funciona
        if 'audio_out' not in globals():
            print("Sistema de audio no inicializado")
            uart.write("ERROR: Sistema de audio no inicializado\n")
            # Enviamos LISTO de todas formas para no bloquear el sistema
            time.sleep(0.5)
            uart.write("LISTO\n")
            return
        
        # Verificar si el archivo existe
        try:
            archivos = os.listdir("/vocales_audio")
            archivo_objetivo = f"{vocal.lower()}.wav"
            if archivo_objetivo not in archivos:
                print(f"Archivo no encontrado: {archivo_objetivo}. Archivos disponibles: {archivos}")
                uart.write("ERROR: Archivo no encontrado\n")
                time.sleep(0.5)
                uart.write("LISTO\n")  # Enviar LISTO para no bloquear el flujo
                return
        except Exception as e:
            print(f"Error al verificar archivos: {e}")
            uart.write(f"ERROR: Al verificar archivos - {e}\n")
            time.sleep(0.5)
            uart.write("LISTO\n")  # Enviar LISTO para no bloquear el flujo
            return
            
        print(f"Reproduciendo: {ruta_audio}")
        
        try:
            # Silenciar cualquier sonido previo enviando unos ms de silencio
            silencio = bytearray(1024)
            audio_out.write(silencio)
            
            with open(ruta_audio, "rb") as file:
                # Leer y validar el encabezado WAV (primeros 44 bytes)
                wav_header = file.read(44)
                
                # Validar formato WAV básico (podría mejorarse para mayor robustez)
                if wav_header[0:4] != b'RIFF' or wav_header[8:12] != b'WAVE':
                    print("Formato de archivo inválido")
                    uart.write("ERROR: Formato de archivo inválido\n")
                    time.sleep(0.5)
                    uart.write("LISTO\n")
                    return
                    
                # Posicionar después del encabezado
                file.seek(44)
                
                # Usar un buffer más pequeño para mayor compatibilidad
                chunk = bytearray(1024)
                
                # Leer y reproducir datos en chunks
                try:
                    while True:
                        bytes_read = file.readinto(chunk)
                        if bytes_read == 0:
                            break
                        audio_out.write(chunk[:bytes_read])
                    
                    # Enviar un poco más de silencio al final para evitar artefactos
                    audio_out.write(silencio)
                except OSError as e:
                    print(f"Error durante la reproducción: {e}")
                    # No interrumpimos el flujo, continuamos
            
            # Enviar confirmación al PC
            uart.write("LISTO\n")
            print("Audio reproducido, enviada confirmación")
        except OSError as e:
            print(f"Error de I2S durante la reproducción: {e}")
            uart.write(f"ERROR: {e}\n")
            time.sleep(0.5)
            uart.write("LISTO\n")  # Enviar LISTO para no bloquear el flujo
    except Exception as e:
        print(f"Error al reproducir audio: {e}")
        uart.write(f"ERROR: {e}\n")
        time.sleep(0.5)
        uart.write("LISTO\n")  # Enviar LISTO para no bloquear el flujo

# Enviar mensaje de inicio para indicar que estamos listos
print("ESP32 iniciado y listo")
uart.write("LISTO\n")

# Bucle principal
while True:
    if uart.any():
        # Leer datos recibidos
        comando = uart.readline().decode('utf-8').strip()
        print(f"Comando recibido: {comando}")
        
        # Procesar comando
        if "Letra_" in comando:
            # Extraer la vocal del comando (formato esperado: "Letra_X")
            vocal = comando.split("_")[1]
            if vocal in ['A', 'E', 'I', 'O', 'U']:
                reproducir_audio(vocal)
            else:
                print(f"Vocal no reconocida: {vocal}")
                uart.write("ERROR: Vocal no reconocida\n")
        else:
            # Si recibimos "HOLA", respondemos con "LISTO"
            if comando == "HOLA":
                uart.write("LISTO\n")
                print("Mensaje de inicialización recibido, enviando LISTO")
    
    # Pequeña pausa para no saturar el CPU
    time.sleep(0.1)

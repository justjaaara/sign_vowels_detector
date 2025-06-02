import sys
import select
import time

print("ESP32 listo para recibir datos desde el PC.")

while True:
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        mensaje = sys.stdin.readline().strip()
        print("Recibido desde el PC:", mensaje)
        if mensaje == "salir":
            print("Deteniendo recepción.")
            break
    time.sleep(0.1)

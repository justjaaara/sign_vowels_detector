import cv2
import os

# importar clase seguimiento Mano
import SeguimientoManos as sm

# Creacion de la carpeta
nombre = 'Letra_E'
direccion = '/home/felipe/Desktop/Vocales/data'
carpeta = direccion + '/' + nombre

if not os.path.exists(carpeta):
    os.makedirs(carpeta)
    print('Carpeta creada:', carpeta)


# lecutra de la cámara

cap = cv2.VideoCapture(0)
#Cambiar resolucion
# cap.set(3, 1280)
# cap.set(4, 720)

# Declaramos el contador
cont = 0

# declara detector

detector = sm.detectormanos(Confdeteccion=0.9)

while True:
    # Realizar la lectura de la cap
    ret, frame = cap.read()

    # Extraer informacion de la mano
    frame = detector.encontrarmanos(frame, dibujar= False)

    #Posicion una sola mano
    lista1, bbox, mano = detector.encontrarposicion(frame, ManoNum=0, dibujarPuntos=False, dibujarBox=False, color=(0, 255, 0))

    # Si hay mano
    if mano ==1:
        #Extraer la inforamción del cuadro
        xmin, ymin, xmax, ymax = bbox

        #Asignamos margen

        xmin=  xmin - 40 
        ymin=  ymin - 40 
        xmax=  xmax + 40 
        ymax=  ymax + 40 

        #Realizar recorte de nuestra mano

        recorte = frame[ymin:ymax, xmin:xmax]

        # Redimensionar la imagen
        # recore = cv2.resize(recorte, (500,500), interpolation=cv2.INTER_CUBIC)

        # Alamcenar nuestras iamgenes
        # cv2.imwrite(carpeta + "/E_{}.jpg".format(cont), recorte)

        cont += 1

        cv2.imshow('Recorte', recorte)

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), [0, 255, 0], 2)


    # Mostrar FPS
    cv2.imshow("LENGUAJE VOCALES", frame)
    # Leer nuestro teclado
    t = cv2.waitKey(1)
    if t == 27 or cont == 100:
        break

cap.release()
cv2.destroyAllWindows()

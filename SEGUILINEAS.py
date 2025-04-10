import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# Configuración de pines
LED_IZQUIERDA = 17
LED_CENTRO = 27
LED_DERECHA = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_IZQUIERDA, GPIO.OUT)
GPIO.setup(LED_CENTRO, GPIO.OUT)
GPIO.setup(LED_DERECHA, GPIO.OUT)

def apagar_todos():
    GPIO.output(LED_IZQUIERDA, GPIO.LOW)
    GPIO.output(LED_CENTRO, GPIO.LOW)
    GPIO.output(LED_DERECHA, GPIO.LOW)

def detectar_direccion(frame):
    frame = cv2.resize(frame, (640, 480))
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    suavizado = cv2.GaussianBlur(gris, (13, 13), 0)
    bordes = cv2.Canny(suavizado, 50, 150)

    altura, ancho = bordes.shape
    izquierda = bordes[:, :ancho//3]
    centro = bordes[:, ancho//3:2*ancho//3]
    derecha = bordes[:, 2*ancho//3:]

    suma_izquierda = np.sum(izquierda)
    suma_centro = np.sum(centro)
    suma_derecha = np.sum(derecha)

    if suma_izquierda > suma_derecha and suma_izquierda > suma_centro:
        direccion = "Girar a la izquierda"
        estado = 'izquierda'
    elif suma_derecha > suma_izquierda and suma_derecha > suma_centro:
        direccion = "Girar a la derecha"
        estado = 'derecha'
    else:
        direccion = "Avanzar recto"
        estado = 'centro'
    
    return direccion, estado, bordes

# Captura de video
cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        direccion, estado, bordes = detectar_direccion(frame)
        print(direccion)

        apagar_todos()  # Apaga todos antes de encender el adecuado

        if estado == 'izquierda':
            GPIO.output(LED_IZQUIERDA, GPIO.HIGH)
        elif estado == 'centro':
            GPIO.output(LED_CENTRO, GPIO.HIGH)
        elif estado == 'derecha':
            GPIO.output(LED_DERECHA, GPIO.HIGH)

        cv2.imshow("Bordes", bordes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

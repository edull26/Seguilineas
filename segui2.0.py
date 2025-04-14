import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# Pines GPIO
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

    # Cortar los 5 cuadrantes
    q1 = bordes[:, 0:140]
    q2 = bordes[:, 140:251]
    q3 = bordes[:, 251:370]
    q4 = bordes[:, 370:481]
    q5 = bordes[:, 481:640]

    # Sumar píxeles en cada cuadrante
    umbral = 50000
    hay_q1 = np.sum(q1) > umbral
    hay_q2 = np.sum(q2) > umbral
    hay_q4 = np.sum(q4) > umbral
    hay_q5 = np.sum(q5) > umbral

    # Lógica de decisión
    if hay_q2 and hay_q4:
        direccion = "Avanzar recto"
        estado = 'centro'
    elif hay_q1 or hay_q2:
        direccion = "Girar a la izquierda"
        estado = 'izquierda'
    elif hay_q4 or hay_q5:
        direccion = "Girar a la derecha"
        estado = 'derecha'
    else:
        direccion = "Sin línea detectada"
        estado = 'ninguno'

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

        apagar_todos()

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

import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# Configuración de pines GPIO
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
    frame = cv2.resize(frame, (640, 480))  # Tamaño estándar
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    suavizado = cv2.GaussianBlur(gris, (13, 13), 0)
    bordes = cv2.Canny(suavizado, 50, 150)

    # Cortamos los cuadrantes relevantes
    q2 = bordes[:, 140:250]  # Borde izquierdo
    q4 = bordes[:, 370:480]  # Borde derecho

    # Calculamos la suma de píxeles blancos (bordes detectados)
    suma_q2 = np.sum(q2)
    suma_q4 = np.sum(q4)

    # Definimos un umbral para considerar si hay borde presente
    umbral = 50000

    hay_izquierda = suma_q2 > umbral
    hay_derecha = suma_q4 > umbral

    # Decisión basada en los cuadrantes
    if hay_izquierda and hay_derecha:
        direccion = "Avanzar recto"
        estado = 'centro'
    elif hay_izquierda:
        direccion = "Girar a la izquierda"
        estado = 'izquierda'
    elif hay_derecha:
        direccion = "Girar a la derecha"
        estado = 'derecha'
    else:
        direccion = "Sin línea detectada"
        estado = 'ninguno'  # No enciende ningún LED

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

        apagar_todos()  # Apaga todos los LEDs antes de decidir

        if estado == 'izquierda':
            GPIO.output(LED_IZQUIERDA, GPIO.HIGH)
        elif estado == 'centro':
            GPIO.output(LED_CENTRO, GPIO.HIGH)
        elif estado == 'derecha':
            GPIO.output(LED_DERECHA, GPIO.HIGH)
        # Si estado == 'ninguno', no se enciende ningún LED

        cv2.imshow("Bordes", bordes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    GPIO.cleanup()

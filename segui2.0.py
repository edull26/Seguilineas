import cv2
import RPi.GPIO as GPIO
import time

# Pines de salida hacia Arduino
PIN_AVANZAR = 17
PIN_IZQUIERDA = 27
PIN_DERECHA = 22

# Configurar GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_AVANZAR, GPIO.OUT)
GPIO.setup(PIN_IZQUIERDA, GPIO.OUT)
GPIO.setup(PIN_DERECHA, GPIO.OUT)

def enviar_senal(avanzar=False, izquierda=False, derecha=False):
    GPIO.output(PIN_AVANZAR, GPIO.HIGH if avanzar else GPIO.LOW)
    GPIO.output(PIN_IZQUIERDA, GPIO.HIGH if izquierda else GPIO.LOW)
    GPIO.output(PIN_DERECHA, GPIO.HIGH if derecha else GPIO.LOW)

# Capturar cámara
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocesamiento de imagen
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # Región de interés (opcional: parte baja de la imagen)
    roi = binary[frame.shape[0]-100:, :]

    # Encontrar contornos
    contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    linea_detectada = False

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cx = x + w // 2

        if 140 <= cx <= 250:
            print("Cuadrante 2: girar izquierda")
            enviar_senal(izquierda=True)
            linea_detectada = True
            break
        elif 251 <= cx <= 369:
            print("Cuadrante 3: avanzar recto")
            enviar_senal(avanzar=True)
            linea_detectada = True
            break
        elif 370 <= cx <= 640:
            print("Cuadrante 4 o 5: girar derecha")
            enviar_senal(derecha=True)
            linea_detectada = True
            break

    if not linea_detectada:
        print("No se detectó línea, detenerse o mantener estado")
        enviar_senal()  # Ninguna señal activa

    # Mostrar la vista para depuración
    cv2.imshow("Vista robot", roi)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Limpieza
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()

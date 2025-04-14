import cv2
import RPi.GPIO as GPIO
import time

# Pines hacia Arduino
PIN_AVANZAR = 17
PIN_IZQUIERDA = 27
PIN_DERECHA = 22

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_AVANZAR, GPIO.OUT)
GPIO.setup(PIN_IZQUIERDA, GPIO.OUT)
GPIO.setup(PIN_DERECHA, GPIO.OUT)

# Función para mandar una sola señal activa
def enviar_senal(avanzar=False, izquierda=False, derecha=False):
    GPIO.output(PIN_AVANZAR, GPIO.HIGH if avanzar else GPIO.LOW)
    GPIO.output(PIN_IZQUIERDA, GPIO.HIGH if izquierda else GPIO.LOW)
    GPIO.output(PIN_DERECHA, GPIO.HIGH if derecha else GPIO.LOW)

# Cámara
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Región de interés (parte baja de la imagen)
    roi = frame[frame.shape[0]-100:, :]

    # Escala de grises
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Filtro Gaussiano para reducir ruido
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Canny para detección de bordes
    edges = cv2.Canny(blur, 50, 150)

    # Contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    linea_detectada = False

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 100:
            continue  # ignorar contornos pequeños

        x, y, w, h = cv2.boundingRect(cnt)
        cx = x + w // 2  # centro X del contorno

        # Determinar cuadrante según cx
        if 140 <= cx <= 250:
            print(f"CX={cx} → Cuadrante 2: girar izquierda")
            enviar_senal(izquierda=True)
            linea_detectada = True
            break
        elif 251 <= cx <= 369:
            print(f"CX={cx} → Cuadrante 3: avanzar recto")
            enviar_senal(avanzar=True)
            linea_detectada = True
            break
        elif 370 <= cx <= 640:
            print(f"CX={cx} → Cuadrante 4 o 5: girar derecha")
            enviar_senal(derecha=True)
            linea_detectada = True
            break

    if not linea_detectada:
        print("No se detectó línea → sin señal")
        enviar_senal()  # Apaga todas las señales

    # Mostrar vista para debug
    cv2.imshow("Canny", edges)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Finalizar
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()


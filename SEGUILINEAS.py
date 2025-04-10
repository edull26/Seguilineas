import cv2
import numpy as np

# Iniciar la captura de video desde la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara.")
    exit()

while True:
    # Capturar un fotograma
    ret, image = cap.read()
    if not ret:
        print("Error: No se pudo capturar el fotograma.")
        break

    # Redimensionar la imagen a un tamaño fijo
    image = cv2.resize(image, (800, 700))

    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar un filtro Gaussiano para reducir el ruido y mejorar la detección de bordes
    img_blur = cv2.GaussianBlur(gray, (9, 9), 3)

    # Aplicar el operador Canny para la detección de bordes
    bordes = cv2.Canny(img_blur, 50, 150)

    # Encontrar contornos en la imagen binaria
    contours, _ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Encontrar el contorno más grande (posiblemente la línea a seguir)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Obtener el centroide del contorno
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Determinar la posición de la línea con respecto al centro de la imagen
            frame_center = image.shape[1] // 2
            if cx < frame_center - 50:
                print("Izquierda")
            elif cx > frame_center + 50:
                print("Derecha")
            else:
                print("Avanza")
        
        # Dibujar el contorno y el centroide en la imagen
        cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 2)
        cv2.circle(image, (cx, cy), 5, (0, 0, 255), -1)

    # Mostrar la imagen en blanco y negro con los bordes detectados
    cv2.imshow('Detección de Bordes', bordes)
    
    # Mostrar la imagen con contornos
    #cv2.imshow('Seguimiento de Línea', image)

    # Salir del bucle si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar la cámara y cerrar las ventanas
cap.release()
cv2.destroyAllWindows()

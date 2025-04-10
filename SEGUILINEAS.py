import cv2
import numpy as np

def detectar_direccion(frame):
    # Convertir a escala de grises
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicar filtro gaussiano para reducir ruido
    suavizado = cv2.GaussianBlur(gris, (13, 13), 0)
    
    # Aplicar detección de bordes
    bordes = cv2.Canny(suavizado, 50, 150)
    
    # Obtener dimensiones de la imagen
    altura, ancho = bordes.shape
    
    # Dividir en tres secciones
    izquierda = bordes[:, :ancho//3]
    centro = bordes[:, ancho//3:2*ancho//3]
    derecha = bordes[:, 2*ancho//3:]
    
    # Contar píxeles blancos (bordes detectados)
    suma_izquierda = np.sum(izquierda)
    suma_centro = np.sum(centro)
    suma_derecha = np.sum(derecha)
    
    # Determinar dirección
    if suma_izquierda > suma_derecha and suma_izquierda > suma_centro:
        direccion = "Girar a la izquierda"
    elif suma_derecha > suma_izquierda and suma_derecha > suma_centro:
        direccion = "Girar a la derecha"
    else:
        direccion = "Avanzar recto"
    
    return direccion, bordes

# Captura de video
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    direccion, bordes = detectar_direccion(frame)
    print(direccion)
    
    # Mostrar la imagen con bordes detectados
    cv2.imshow("Bordes", bordes)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

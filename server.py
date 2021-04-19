import socket
# import PySimpleGUI as sg
import threading
import hashlib
import time
import logging
import datetime
import sys
import os
from collections import deque

# Log Config ------------------------------------
date = datetime.datetime.now()
date = date.strftime("%Y-%b-%d-%H-%M-%S")
logging.basicConfig(format='%(asctime)s - %(message)s', filename=("./Logs/Server/" + date + "-log.txt"),
                    level=logging.DEBUG)

# Interfaz --------------------------------------

tamanioArchivo = int(sys.argv[1])
maxConexiones = int(sys.argv[2])
print(tamanioArchivo)
print(maxConexiones)

# =============================================================================
# layout = [
#     [sg.Text("Elija el tamaño del archivo (en MB)"), ],
#     [sg.Listbox(values=[100, 250], enable_events=True, size=(20, 2), key="-ARCHIVO-")],
#     [sg.Text("Elija la cantidad de clientes en simultáneo"), ],
#     [sg.InputText(size=(30, 1), key="-CONEXIONES-")],
#     [sg.Button("Ok")]
# ]
# window = sg.Window("Servidor", layout)
# 
# while True:
#     # Manejo básico de la interfaz.
#     event, values = window.read()
#     if event == "Ok":
#         tamanioArchivo = values["-ARCHIVO-"]
#         maxConexiones = int(values["-CONEXIONES-"])
#         # Verificación del número de conexiones.
#         if len(tamanioArchivo) == 0:
#             sg.Popup("Seleccione un archivo", keep_on_top=True)
#         elif maxConexiones > 25:
#             sg.Popup("Inserte un número de conexiones menor o igual a 25", keep_on_top=True)
#         else:
#             window.close()
#             break
#     elif event == sg.WIN_CLOSED:
#         quit()
# =============================================================================

if tamanioArchivo == 100:
    rutaArchivo = "data/prueba1.txt"
else:
    rutaArchivo = "data/prueba2.txt"

logging.info("Nombre del archivo: " + "prueba1.txt" if tamanioArchivo == 100 else "prueba2.txt")
logging.info(
    "Tamaño del archivo a enviar: " + str(os.stat("data/prueba1.txt").st_size if tamanioArchivo == 100 else os.stat(
        "data/prueba2.txt").st_size) + "Bytes")
# Lógica --------------------------------------

# Dirección y puertos usados para cada servicio.
localIP = "127.0.0.1"
puertoTcp = 20005
puertoUdp = 20006
# Tamaño máximo del buffer en cada servicio.
bufferTcp = 1024
bufferUdp = 65507

# Establecimiento del puerto TCP.
tcpSocket = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
tcpSocket.bind((localIP, puertoTcp))
tcpSocket.listen()
# Cola de las conexiones en espera
conexiones = deque()
# Establecimiento del puerto UDP.
udpSocket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)
udpSocket.bind((localIP, puertoUdp))


# Función que ejecuta un thread para manejar el envío de un archivo a un cliente.
def client_thread(conexionActual, index):
    logging.info("Empezo la transferencia pare el Cliente " + str(index))
    print("Inicio la transferencia para el Cliente", index)
    # Init digest para generar el hash
    h = hashlib.sha256()
    # Se envía la información TCP.
    conexionActual[0].send(str(index).encode())
    conexionActual[0].send(str(maxConexiones).encode())
    # Se recibe un mensaje de UDP del cliente para recuperar su dirección UDP.
    cliente = udpSocket.recvfrom(bufferTcp)
    # Se abre el stream del archivo pa' enviar.
    archivo = open(rutaArchivo, "rb")
    # Esta i es solo para saber cuántos paquetes se terminan enviando (al otro lado podemos contar, creo). 
    i = 0
    start = time.time_ns() / 1000000
    while True:
        fragmento = archivo.read(bufferUdp)
        i += 1
        if not fragmento: break
        udpSocket.sendto(fragmento, cliente[1])
        h.update(fragmento)
    end = time.time_ns() / 1000000
    logging.info("Cantidad de paquetes enviados para el Cliente " + str(index) + ": " + str(i))
    logging.info("Tiempo total que tomo el envio para el Cliente " + str(index) + ": " + str(end - start) + "millis")
    # Envio de hash del archivo por TCP
    hsh = h.hexdigest()
    conexionActual[0].send(hsh.encode())
    # Recibe el estado en que llego el archivo
    state = conexionActual[0].recv(bufferTcp).decode()
    if state == "OK":
        logging.info("El Cliente " + str(index) + " recibio correctamente el archivo")
    else:
        logging.info("El Cliente " + str(index) + " recibio incorrectamente el archivo")

    print("El Cliente " + str(index) + " finalizo")
    conexionActual[0].close()


# Ciclo que maneja el estado constante del servidor.
while True:
    # Se esperan conexiones TCP constantemente.
    conexiones.append(tcpSocket.accept())
    print("Cliente aceptado")
    # Se espera hasta tener el número solicitado de conexiones.
    if len(conexiones) >= maxConexiones:
        for i in range(maxConexiones):
            conexionActual = conexiones.popleft()
            threading.Thread(target=client_thread, args=(conexionActual, i + 1,)).start()
        break

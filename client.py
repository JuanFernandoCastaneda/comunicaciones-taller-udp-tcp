import socket
import select
import time
import os
import hashlib
import logging
import datetime
import sys

# Log Config ------------------------------------
date = datetime.datetime.now()
date = date.strftime("%Y-%b-%d-%H-%M-%S")
logging.basicConfig(format='%(asctime)s - %(message)s', filename=("./Logs/Client/" + date + "-log.txt"),
                    level=logging.DEBUG)

# Dirección y puertos usados para cada servicio.
localIP = sys.argv[1]  # IP del servidor
puertoTcp = 20005
puertoUdp = 20006
# Tamaño máximo del buffer en cada servicio.
bufferTcp = 1024
bufferUdp = 65507
# Tiempo (creo que en segundos) que espera la conexión UDP para cerrarse después de no recibir más mensajes.
timeout = 5

# Establecimiento y conexión puerto TCP con el servidor.
tcpSocket = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
tcpSocket.connect((localIP, puertoTcp))
logging.info("Puerto TCP del cliente: " + str(tcpSocket.getsockname()[1]))
# Creación cascarón puerto UDP.
udpSocket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

# Recepción del mensaje TCP con el id del cliente y apertura del stream con el archivo. 
id = tcpSocket.recv(bufferTcp).decode()
numClientes = tcpSocket.recv(bufferTcp).decode()
PATH_FILE = "recibidos/Cliente" + id + "-Prueba-" + numClientes + ".txt"
print("Mensaje TCP (id): " + id, flush=True)
logging.info("id cliente: " + id)
archivo = open(PATH_FILE, "wb")

# Envío de mensaje sin importancia al servidor a través de UDP para posibilitar la conexión.
udpSocket.sendto(b"Hi", (localIP, puertoUdp))
logging.info("Puerto UDP del cliente: " + str(udpSocket.getsockname()[1]))
print("Cliente esperando por respueta del servidor...", flush=True)

h = hashlib.sha256()

start, end = 0, 0
first = True
paquetes = 0
# Ciclo que maneja la recepción del archivo enviado por UDP.
while True:
    # Aquí lo importante es que se incluye el parámetro timeout.
    ready = select.select([udpSocket], [], [], timeout)
    # Ready parece ser si el puerto UDP envió algo antes del timeout.
    if ready[0]:
        if first:
            start = time.time() * 1000
        datagramaActual = udpSocket.recv(bufferUdp)
        archivo.write(datagramaActual)
        h.update(datagramaActual)
        first = False
        paquetes += 1
    else:
        size = os.stat(PATH_FILE).st_size
        end = time.time() * 1000
        logging.info("Archivo " + id + " guardado en" + PATH_FILE)
        logging.info("Cantidad de paquetes recibidos del archivo " + id + ": " + str(paquetes) + " paquetes")
        print("Tamaño del Archivo", id, "recibido", size, "Bytes")
        logging.info("Cantidad de bytes recibidos archivo " + id + ": " + str(size) + " Bytes")
        logging.info("El tiempo total de la transferencia fue de " + str(end - start) + "ms")
        archivo.close()
        break

hash_server = tcpSocket.recv(bufferTcp).decode()
hash_client = h.hexdigest()

if hash_server == hash_client:
    print("Archivo correcto")
    logging.info("Archivo recibido correctamente, codigos hash coinciden")
    tcpSocket.send("OK".encode())
else:
    print("Archivo incorrecto")
    logging.info("Archivo recibido incorrectamente, codigos hash no coinciden")
    tcpSocket.send("NOT OK".encode())

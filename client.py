import socket
import select

# Dirección y puertos usados para cada servicio.
localIP = "127.0.0.1"
puertoTcp = 20001
puertoUdp = 20002
# Tamaño máximo del buffer en cada servicio.
bufferTcp = 1024
bufferUdp = 65507
# Tiempo (creo que en segundos) que espera la conexión UDP para cerrarse después de no recibir más mensajes.
timeout = 2

# Establecimiento y conexión puerto TCP con el servidor.
tcpSocket = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
tcpSocket.connect((localIP, puertoTcp))
# Creación cascarón puerto UDP.
udpSocket = socket.socket(socket.AF_INET, type=socket.SOCK_DGRAM)

# Recepción del mensaje TCP con el id del cliente y apertura del stream con el archivo. 
id = tcpSocket.recv(bufferTcp).decode()
print("Mensaje TCP (id): " + id, flush=True)
archivo = open("recibidos/archivo"+id+".txt", "wb")

# Envío de mensaje sin importancia al servidor a través de UDP para posibilitar la conexión.
udpSocket.sendto(b"Hi", (localIP, puertoUdp))

# Ciclo que maneja la recepción del archivo enviado por UDP.
while True:
    # Aquí lo importante es que se incluye el parámetro timeout. 
    ready = select.select([udpSocket], [], [], timeout)
    # Ready parece ser si el puerto UDP envió algo antes del timeout.
    if ready[0]:
        datagramaActual = udpSocket.recv(bufferUdp)
        archivo.write(datagramaActual)
    else:
        archivo.close()
        break

print("Archivo "+id+" enviado.", flush=True)


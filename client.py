import socket
import os
import time
import sys

# Constants
UDP_IP = "127.0.0.1"
UDP_PORT = 8000
BITS_SEQUENCE = 3
WINDOW_SIZE = 2**BITS_SEQUENCE
PACKAGE_SIZE = 1
TIMEOUT = 1
MAX_RT = 10
alpha = 0.125
beta = 0.25

# Message format = "ACK-BIT|||SEQUENCE-NUMBER|||FIN-BIT|||PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
FIN_HEADER = "1"
FIN_FALSE = "0"
SEPARATOR = "|||"
data = ""
addr = ""
TwoWH = sys.argv[1]
ThreeWH = sys.argv[2]
savesend = True
resend = False
Close = True
Conn = True
RS = False

# File open and size
file = open("tarea2.txt","rb")
file_size = os.stat("tarea2.txt").st_size

# Variables
count = 0
base = 0
nextseqnum = 0
received = 0
transm = 0
#n_transm = 0
time_send = 0
time_ack = 0
devRTT = 0
estimatedRTT = 0

# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Buffer
package = []

# Algoritmo de Karn
def setTimeout(s_rtt, estimatedRTT, devRTT):
    # RTT estimado
    sampleRTT = s_rtt
    estimatedRTT = (1-alpha)*estimatedRTT + alpha*sampleRTT
    # Desviacion estandar
    if ((sampleRTT - estimatedRTT) < 0):
        devRTT = (1-beta)*devRTT + beta*(estimatedRTT-sampleRTT)
    else:
        devRTT = (1-beta)*devRTT + beta*(sampleRTT-estimatedRTT)
    #Calculo del Timeout
    timeout = estimatedRTT + 4*devRTT
    return timeout

# Two way handshake
while TwoWH:
    # SYN
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+FIN_FALSE+SEPARATOR+str(WINDOW_SIZE-1))
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    # SYN-ACK
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    if (int(datalist[0]) and int(datalist[1])==base):
        TwoWH = False

# Three way handshakeSEPARATOR+
while ThreeWH:
    # SYN
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+FIN_FALSE+SEPARATOR+str(WINDOW_SIZE-1))
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    # SYN-ACK
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    #print (datalist)
    if (int(datalist[0]) and int(datalist[1])==base):
        base += 1
        # ACK
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(base)+SEPARATOR+FIN_FALSE+SEPARATOR+"ACK")
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        ThreeWH = False
    base = 0

print ("Conexion con el servidor establecida con exito")

tiempo_inicio = time.time()

while Conn:
    if transm > MAX_RT:
        print("Closed connection with server")
        Close = False
        Conn = False
        break
    package = package[received:]
    while savesend:
        p = file.read(PACKAGE_SIZE).decode("utf-8")
        if p != '':
            package.append(p)
            pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+FIN_FALSE+SEPARATOR+p)
            time_send = time.time()
            sock.sendto(pkt, (UDP_IP, UDP_PORT))
        if (nextseqnum == base):
            sock.settimeout(TIMEOUT)
        nextseqnum = (nextseqnum + 1) % WINDOW_SIZE
        if received != 0:
            received -= 1
        if nextseqnum == (base + WINDOW_SIZE) % WINDOW_SIZE and received == 0:
            savesend = False
    i = base
    j = 0
    while resend:
        print ("Retransmitiendo")
        i = (i + j) % WINDOW_SIZE
        if (i == base):
            transm += 1
            n_transm += transm
            sock.settimeout(TIMEOUT)
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(i)+SEPARATOR+FIN_FALSE+SEPARATOR+package[j])
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        j += 1
        if j == WINDOW_SIZE:
            resend = False
            print ("No mas retransmisiones")
    try:
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        #print (datalist)
        if int(datalist[0]):
            nseqr = (int(datalist[1]) + 1) % WINDOW_SIZE
            time_ack = time.time()
            rtt = (time_ack - time_send)
            TIMEOUT = setTimeout(rtt, estimatedRTT, devRTT)
            received = 0
            transm = 0
            if (nseqr == nextseqnum): # All ACK'd
                sock.settimeout(None)
                savesend = True
                received = WINDOW_SIZE
                count += received * PACKAGE_SIZE
                base = nseqr
            else: # Some ACK'd
                sock.settimeout(TIMEOUT)
                savesend = True
                while base != nseqr:
                    received += 1
                    base = (base + 1) % WINDOW_SIZE
                count += received * PACKAGE_SIZE
    except Exception as e:
        print(e)
        if not(RS):
            TIMEOUT *= 2
        RS = True
        savesend = False
        resend = True
        continue
    # Texto finalizado
    if (count >= file_size):
        sock.settimeout(None)
        Conn = True
        break

tiempo_final = time.time()
tiempo_envio = tiempo_final - tiempo_inicio

print ("Envio realizado con exito")

# Close conection client
while Close:
    # FIN_CLIENT
    nextseqnum = (nextseqnum + 1) % WINDOW_SIZE
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+FIN_HEADER+SEPARATOR+"FIN_CLIENT")
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    nextseqnum = (nextseqnum + 1) % WINDOW_SIZE
    # ACK_SERVER
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    if (int(datalist[0]) and int(datalist[2])):
        # FIN_SERVER
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        if int(datalist[2]):
            # ACK_CLIENT
            pkt = str.encode(ACK_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+FIN_HEADER+SEPARATOR+"ACK_CLIENT")
            sock.sendto(pkt, (UDP_IP, UDP_PORT))
            Close = False
            file.close()
            sock.close()
            print("Conexion con el servidor cerrada con exito")
            break

print("Tiempo de envio: " + str(tiempo_envio))
print("Numero de retransmisiones: " + str(n_transm))

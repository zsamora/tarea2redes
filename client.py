import socket
import os
import time
import sys
# Constants
UDP_IP = "127.0.0.1"
UDP_PORT = 8000
BITS_SEQUENCE = 3
WINDOW_SIZE = 2**BITS_SEQUENCE
MAX_NSEQ = WINDOW_SIZE * 2
PACKAGE_SIZE = 1
SYN_TIMEOUT = 2
TIMEOUT = 1
MAX_RT = 5
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
TwoWH = False#False#sys.argv[1]
ThreeWH = True#True#sys.argv[2]
savesend = True
resend = False
Conn = True
Close = True
NO_ACK = True
RT = False
FIRST_SENT = True

# File open and size
file = open("tarea2.txt","rb")
file_size = os.stat("tarea2.txt").st_size

# Variables
count = 0
base = 0
nextseqnum = 0
received = 0
transm = 0
n_transm = 0
time_send = 0
time_ack = 0
devRTT = 0
estimatedRTT = 0

# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Buffer
package = []

# Algoritmo de Karn
def setTimeout(s_rtt):
    # RTT estimado
    global estimatedRTT, devRTT
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
    print("Two way handshake")
    if transm > MAX_RT:
        print("Can't stablish conection with server")
        sock.settimeout(None)
        Conn = False
        Close = False
        file.close()
        sock.close()
        break

    sock.settimeout(SYN_TIMEOUT) # 2 segundos entre cada retransmision del paquete SYN
    try:
        # SYN
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+FIN_FALSE+SEPARATOR+str(MAX_NSEQ-1))
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        # SYN-ACK
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print (datalist)
        if (int(datalist[0]) and int(datalist[1])==base):
            sock.settimeout(None)
            transm = 0
            TwoWH = False
            print ("Conexion con el servidor establecida con exito")
    except Exception as e:
        print(e)
        transm += 1

# Three way handshake
while ThreeWH:
    #print("Three way handshake")
    if transm > MAX_RT:
        print("Can't stablish conection with server")
        sock.settimeout(None)
        Conn = False
        Close = False
        file.close()
        sock.close()
        break

    sock.settimeout(SYN_TIMEOUT) # 2 segundos entre cada retransmision del paquete SYN
    try:
        # SYN
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+FIN_FALSE+SEPARATOR+str(MAX_NSEQ-1))
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        # SYN-ACK
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print (datalist)
        if (int(datalist[0]) and int(datalist[1])==base):
            base += 1
            # ACK
            pkt = str.encode(ACK_HEADER+SEPARATOR+str(base)+SEPARATOR+FIN_FALSE+SEPARATOR+"ACK")
            sock.sendto(pkt, (UDP_IP, UDP_PORT))
            sock.settimeout(None)
            transm = 0
            ThreeWH = False
            print ("Conexion con el servidor establecida con exito")
        base = 0
    except Exception as e:
        print(e)
        transm += 1


tiempo_inicio = time.time()
while Conn:
    if transm > MAX_RT:
        print("Closed connection with server")
        sock.settimeout(None)
        Close = False
        Conn = False
        file.close()
        sock.close()
        break
    print("base:",base,"nextseqnum:",nextseqnum,"timeout:", TIMEOUT, "received:",received, "lenpack:",len(package))
    if (received != 0):
        package = package[received:]
    while savesend:
        p = file.read(PACKAGE_SIZE).decode("utf-8")
        # Envio del paquete p
        if (p!=''):
            package.append(p)
            pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+FIN_FALSE+SEPARATOR+p)
            sock.sendto(pkt, (UDP_IP, UDP_PORT))
        # Si se envia por primera vez
        if base == nextseqnum:
            sock.settimeout(TIMEOUT)
            time_send = time.time()
        nextseqnum = (nextseqnum + 1) % MAX_NSEQ
        if received != 0:
            received -= 1
        if nextseqnum == (base + WINDOW_SIZE) % MAX_NSEQ and received == 0:
            savesend = False
    i = base
    j = 0
    while resend:
        i = (i + j) % MAX_NSEQ
        if (i == base):
            transm += 1
            n_transm += 1
            RT = True
            sock.settimeout(TIMEOUT)
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(i)+SEPARATOR+FIN_FALSE+SEPARATOR+package[j])
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        j += 1
        if j == len(package):
            resend = False
    try:
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print (datalist)
        if int(datalist[0]):
            nseqr = (int(datalist[1]) + 1) % MAX_NSEQ
            if not(RT):
                time_ack = time.time()
                rtt = (time_ack - time_send)
                #print("rtt:",rtt)
                TIMEOUT = setTimeout(rtt)
            NO_ACK = False
            RT = False
            #FIRST_SENT = True
            received = 0
            transm = 0
            if (nseqr == nextseqnum): # All ACK'd
                print("ALL ACKD")
                sock.settimeout(None)
                savesend = True
                received = WINDOW_SIZE
                count += received * PACKAGE_SIZE
                base = nseqr
            else: # Some ACK'd
                print("SOME ACKED")
                sock.settimeout(TIMEOUT)
                time_send = time.time()
                print("base",base,"nseqr",nseqr)
                if (base == nseqr):
                    savesend = False
                else:
                    savesend = True
                while base != nseqr:
                    received += 1
                    base = (base + 1) % MAX_NSEQ
                count += received * PACKAGE_SIZE
    except Exception as e:
        print(e)
        if NO_ACK:
            TIMEOUT *= 2
        received = 0
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

# Close conection client
while Close:
    if transm > MAX_RT:
        print("Can't close conection with server")
        sock.settimeout(None)
        Conn = False
        Close = False
        file.close()
        sock.close()
        break
    sock.settimeout(SYN_TIMEOUT) # 2 segundos entre cada retransmision del paquete FIN
    try:
        # FIN_CLIENT
        nextseqnum = (nextseqnum + 1) % MAX_NSEQ
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+FIN_HEADER+SEPARATOR+"FIN_CLIENT")
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        nextseqnum = (nextseqnum + 1) % MAX_NSEQ
        # ACK_SERVER
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print(datalist)
        if (int(datalist[0]) and int(datalist[2])):
            # FIN_SERVER
            data, addr = sock.recvfrom(1024)
            datalist = data.decode("utf-8").split(SEPARATOR)
            print(datalist)
            if int(datalist[2]):
                sock.settimeout(None)
                transm = 0
                # ACK_CLIENT
                pkt = str.encode(ACK_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+FIN_HEADER+SEPARATOR+"ACK_CLIENT")
                sock.sendto(pkt, (UDP_IP, UDP_PORT))
                Close = False
                file.close()
                sock.close()
                print("Conexion con el servidor cerrada con exito")
                print("Tiempo de envio: " + str(tiempo_envio))
                print("Numero de retransmisiones: " + str(n_transm))
                break
    except Exception as e:
        print(e)
        transm +=1

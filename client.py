import socket
import os

# Constants
UDP_IP = "127.0.0.1"
UDP_PORT = 8000
BITS_SEQUENCE = 3
WINDOW_SIZE =2**BITS_SEQUENCE - 1
#SENT_SIZE = WINDOW_SIZE  / 2
PACKAGE_SIZE = 1
TIMEOUT = 1
time_send = 0
time_ack = 0
alpha = 0.125
beta = 0.25
devRTT = 0
estimatedRTT = 0

# Message format = "ACK-BIT|||SEQUENCE-NUMBER|||PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
SEPARATOR = "|||"
TwoWH = False
ThreeWH = True
Conn = True
save = True
resend = False
# File open and size
file = open("tarea2.txt","rb")
file_size = os.stat("tarea2.txt").st_size
# Variables
count = 0
sent = 0
base = 0
nextseqnum = 0
# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
package = []

# Algoritmo de Karn
def setTimeout(s_rtt):
    # RTT estimado
    sampleRTT = s_rtt
    estimatedRTT = (1-alpha)*estimatedRTT + alpha*sampleRTT
    # Desviacion estandar
    if ((sampleRTT - estimatedRTT) < 0)
        devRTT = (1-beta)*devRTT + beta*(estimatedRTT-sampleRTT)
    else:
        devRTT = (1-beta)*devRTT + beta*(sampleRTT-estimatedRTT)
    #Calculo del Timeout
    timeout = estimatedRTT + 4*devRTT
    return timeout

# Two way handshake
while TwoWH:
    # SYN
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+str(WINDOW_SIZE))
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    # SYN-ACK
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    print(datalist)
    if (int(datalist[0]) and int(datalist[1])==base):
        TwoWH = False

# Three way handshake
while ThreeWH:
    # SYN
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+str(WINDOW_SIZE))
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    # SYN-ACK
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    print(datalist)
    if (int(datalist[0]) and int(datalist[1])==base):
        base += 1
        # ACK
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(base)+SEPARATOR+"ACK")
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        ThreeWH = False
    base = 0

while Conn:
    #package = package[base:]
    while save:
        package.append(file.read(PACKAGE_SIZE))
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+package[nextseqnum])
        time_send = time.clock()
        sock.sendto(pkt, (UDP_IP, UDP_PORT_CLIENT))
        if base == nextseqnum:
            sock.settimeout(TIMEOUT)
        nextseqnum += 1
        if nextseqnum > base + WINDOW_SIZE:
            nextseqnum = nextseqnum % WINDOW_SIZE
            save = False

    i = base
    j = 0
    while resend:
        i = (i + j) % WINDOW_SIZE
        if (i == base):
            sock.settimeout(TIMEOUT)
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(nseq)+SEPARATOR+package[i])
        sock.sendto(pkt, (UDP_IP, UDP_PORT_CLIENT))
        j += 1
        if j > WINDOW_SIZE:
            resend = False
    try:
        data, addr = sock.recvfrom(1024)
        time_ack = time.clock()
        rtt = (time_ack - time_send)
        TIMEOUT = setTimeout(rtt)
        datalist = data.decode("utf-8").split(SEPARATOR)
        if int(datalist[0]):
            base = (int(datalist[1]) + 1) % WINDOW_SIZE
            if (base == nextseqnum): # All ACK'd
                sock.settimeout(None)
                save = True
                count += WINDOW_SIZE * PACKAGE_SIZE
            else: # Some ACK'd
                sock.settimeout(TIMEOUT)
                save = True
                count += received # Se suman los ACKed
    except:
        continue
    # Texto finalizado
    if (count >= file_size):
        Conn = False
## Close conection
file.close()
sock.close()

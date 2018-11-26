import socket
import os
import time

# Constants
UDP_IP = "127.0.0.1"
UDP_PORT = 8000
BITS_SEQUENCE = 3
WINDOW_SIZE = 2**BITS_SEQUENCE
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
savesend = True
resend = False
# File open and size
file = open("tarea2.txt","rb")
file_size = os.stat("tarea2.txt").st_size
# Variables
count = 0
base = 0
nextseqnum = 0
received = 0
package = []
# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Algoritmo de Karn
def setTimeout(s_rtt):
    # RTT estimado
    sampleRTT = s_rtt
    estimatedRTT = (1-alpha)*estimatedRTT + alpha*sampleRTT
    # Desviacion estandar
    if ((sampleRTT - estimatedRTT) < 0):
        devRTT = (1-beta)*devRTT + beta*(estimatedRTT-sampleRTT)
    else:
        devRTT = (1-beta)*devRTT + beta*(sampleRTT-estimatedRTT)
    # Calculo del Timeout
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
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(base)+SEPARATOR+str(WINDOW_SIZE-1))
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    # SYN-ACK
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    #print(datalist)
    if (int(datalist[0]) and int(datalist[1])==base):
        base += 1
        # ACK
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(base)+SEPARATOR+"ACK")
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        ThreeWH = False
    base = 0

while Conn:
    package = package[received:]
    while savesend:
        p = file.read(PACKAGE_SIZE).decode("utf-8")
        package.append(p)
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+p)
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        if (nextseqnum == base):
            sock.settimeout(TIMEOUT)
            time_send = time.process_time()
        nextseqnum = (nextseqnum + 1) % WINDOW_SIZE
        if received != 0:
            received -= 1
        if nextseqnum == (base + WINDOW_SIZE) % WINDOW_SIZE and received == 0:
            savesend = False
    i = base
    j = 0
    while resend:
        i = (i + j) % WINDOW_SIZE
        if (i == base):
            sock.settimeout(TIMEOUT)
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(i)+SEPARATOR+package[j])
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
        time_send = time.process_time()
        j += 1
        if j == WINDOW_SIZE:
            resend = False
    try:
        data, addr = sock.recvfrom(1024)
        time_ack = time.process_time()
        rtt = (time_ack - time_send)
        print(setTimeout(rtt))
        #TIMEOUT = setTimeout(rtt)
        datalist = data.decode("utf-8").split(SEPARATOR)
        if int(datalist[0]):
            nseqr = (int(datalist[1]) + 1) % WINDOW_SIZE
            received = 0
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
        savesend = False
        resend = True
        continue
    # Texto finalizado
    if (count >= file_size):
        Conn = False
## Close conection
file.close()
sock.close()

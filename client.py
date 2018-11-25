import socket
import os

# Constants
UDP_IP = "127.0.0.1"
UDP_PORT = 8000
#UDP_PORT_SERVER = 8001
BITS_SEQUENCE = 3
WINDOW_SIZE =2**BITS_SEQUENCE - 1
#SENT_SIZE = WINDOW_SIZE  / 2
PACKAGE_SIZE = 1
TIMEOUT = 0.5

# Message format = "ACK-BIT|||SEQUENCE-NUMBER|||PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
SEPARATOR = "|||"
TwoWH = False
ThreeWH = True
Conn = False#True
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
#sock.bind((UDP_IP, UDP_PORT_CLIENT))
package = [""]*WINDOW_SIZE # Buffer

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
    while save:
        package[nextseqnum] = file.read(PACKAGE_SIZE)
        pkt = str.encode(PKG_HEADER+SEPARATOR+str(nextseqnum)+SEPARATOR+package[nextseqnum])
        sock.sendto(pkt, (UDP_IP, UDP_PORT_CLIENT))
        if base == nextseqnum: # Base dio la vuelta entera o no hay ACK's aun
            sock.settimeout(0.5) # 0.5 seg
        nextseqnum += 1
        if nextseqnum > base + WINDOW_SIZE:
            nextseqnum = nextseqnum % WINDOW_SIZE
            save = False
    i = base
    j = 0
    while resend:
        i += j
        if (i == base):
            sock.settimeout(0.5)
        sock.sendto(str.encode(PKG_HEADER+SEPARATOR+str(nseq)+SEPARATOR+package[i]), (UDP_IP, UDP_PORT_CLIENT))
        j += 1
        if j == WINDOW_SIZE:
            resend = False
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        datalist = data.decode("utf-8").split(SEPARATOR)
        if int(datalist[0]):
            #recnseq = (int(datalist[1]) + 1) % 5 # nseq multiplo de 5
            base = int(datalist[1])
            if base == -1:
                save = False
            elif (base == nextseqnum):
                sock.settimeout(None)
                save = True
            else:
                sock.settimeout(0.5) # 0.5 seg
                save = True
    except:
        continue

    count += received # Se suman los ACKed
    # Texto finalizado
    if (count >= file_size):
        Conn = False
## Close conection
file.close()
sock.close()

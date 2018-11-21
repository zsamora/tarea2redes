import socket
import os

# Constants
UDP_IP = "127.0.0.1"
UDP_PORT_CLIENT = 8000
UDP_PORT_SERVER = 8001
UDP_PORT_RECEIVER = 0
WINDOW_SIZE = 5
PACKAGE_SIZE = 1
INITIAL_TIMEOUT = 1000
# Message format = "ACK-BIT,SEQUENCE-NUMBER,PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
SEPARATOR = ","
nseq = -1
TwoWH = False
ThreeWH = True
Conn = False

file = open("tarea2.txt","r")
size = os.stat("tarea2.txt").st_size
# Variables
count = 0
i = 0
# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT_CLIENT))
# Two way handshake
while TwoWH:
    # SYN
    sock.sendto(str.encode(PKG_HEADER+SEPARATOR+str(nseq+1)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT))
    # SYN-ACK
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print(data.decode("utf-8"),addr)

# Three way handshake
while ThreeWH:
    # SYN
    nseq = nseq + 1 # nseq = 0
    sock.sendto(str.encode(PKG_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT_SERVER))
    # SYN-ACK
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    datalist = data.decode("utf-8").split(",")
    print(data)
    if (not(int(datalist[0])) or int(datalist[1])<nseq): # Not ACK or seq number of package < nseq
        nseq = -1
        continue
    nseq = nseq + 1
    # ACK
    sock.sendto(str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT_SERVER))
    ThreeWH = False

## Package sending
#while (count < size):
while Conn:
    # Envio de paquetes
    while i < WINDOW_SIZE:
        sock.sendto(str.encode(file.read(PACKAGE_SIZE)), (UDP_IP, UDP_PORT_CLIENT))
        sent[i] = True
        i += 1
    # Recibo de ACK's
    sock.bind((UDP_IP, UDP_PORT))

    if sent == WINDOW_SIZE:
        wait()

    count += WINDOW_SIZE
## Close conection

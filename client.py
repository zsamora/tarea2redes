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
sent = 1
# Socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT_CLIENT))
package = [""]*5

# Two way handshake
while TwoWH:
    # SYN
    nseq = nseq + 1 # nseq = 0
    sock.sendto(str.encode(PKG_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT_SERVER))
    # SYN-ACK
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    datalist = data.decode("utf-8").split(SEPARATOR)
    print(datalist)
    if (not(int(datalist[0])) or int(datalist[1])<nseq): # Not ACK or seq number of package < nseq
        nseq = -1
        continue
    nseq += 1 # nseq = 1
    ThreeWH = False

# Three way handshake
while ThreeWH:
    # SYN
    nseq = nseq + 1 # nseq = 0
    sock.sendto(str.encode(PKG_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT_SERVER))
    # SYN-ACK
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    datalist = data.decode("utf-8").split(SEPARATOR)
    print(datalist)
    if (not(int(datalist[0])) or int(datalist[1])<nseq): # Not ACK or seq number of package < nseq
        nseq = -1
        continue
    nseq += 1 # nseq = 1
    # ACK
    sock.sendto(str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"ACK"), (UDP_IP, UDP_PORT_SERVER))
    nseq += 1 # nseq = 2
    ThreeWH = False

## Package sending
nseq = 0
while Conn:
    sent = 0
    # Se recibio un ACK o más
    if nseq != 0:
        print()
    # Envio de paquetes
    while nseq < WINDOW_SIZE:
        package[nseq] = PKG_HEADER+SEPARATOR+str(nseq)+SEPARATOR+file.read(PACKAGE_SIZE)
        sock.sendto(str.encode(package[nseq]), (UDP_IP, UDP_PORT_CLIENT))
        nseq += 1
        sent += 1
    count += sent
    # Recibo de ACK's
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    datalist = data.decode("utf-8").split(SEPARATOR)
    if int(datalist[0]):
        nseq = (int(datalist[1]) + 1) % 5 # nseq multiplo de 5

    if (count < size):
        Conn = False
## Close conection
file.close()
sock.close()

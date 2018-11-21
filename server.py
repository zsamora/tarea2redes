import socket

UDP_IP = "127.0.0.1"
UDP_PORT_CLIENT = 8000
UDP_PORT_SERVER = 8001
WINDOW_RECEIVE = []
file = open("tarea2res.txt","w")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Message format = "ACK-BIT,SEQUENCE-NUMBER,PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
SEPARATOR = ","
nseq = -1
TwoWH = False
ThreeWH = True
Conn = False
sock.bind((UDP_IP, UDP_PORT_SERVER))

# Two way handshake
while TwoWH:
    # SYN
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print(data.decode("utf-8"),addr)
    # SYN-ACK
    sock.sendto(str.encode(ACK_HEADER+SEPARATOR+str(nseq+1)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT))


# Three way handshake
while ThreeWH:
    # SYN
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    datalist = data.decode("utf-8").split(",")
    print(data)
    # Failed or corrupted SYN
    if (int(datalist[0])): # Si el paquete es ACK
        sock.sendto(str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT_CLIENT))
        continue
    # SYN-ACK
    nseq += 1 # nseq = 0
    sock.sendto(str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN"), (UDP_IP, UDP_PORT_CLIENT))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print(data.decode("utf-8"),addr)
    if nseq == 1:
        ThreeWH = False


while Conn:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    file.write(data.decode("utf-8"))
    #print(data.decode("utf-8"))
    if not(data):
        break
file.close()

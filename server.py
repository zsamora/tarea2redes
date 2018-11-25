import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8000
file = open("tarea2res.txt","w")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Message format = "ACK-BIT,SEQUENCE-NUMBER,PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
SEPARATOR = "|||"
TwoWH = False
ThreeWH = True
Conn = False#True
# Variables
MAX_NSEQ = 0
expected_seqn = 0

sock.bind((UDP_IP, UDP_PORT))

# Two way handshake
while TwoWH:
    # SYN
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    # SYN-ACK
    nseq = int(datalist[1])
    if (expected_seqn == nseq):
        MAX_NSEQ = int(datalist[2])
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN-ACK")
        sock.sendto(pkt, addr)
        TwoWH = False


# Three way handshake
while ThreeWH:
    # SYN
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    print(datalist)
    # SYN-ACK
    nseq = int(datalist[1])
    if (expected_seqn == nseq):
        MAX_NSEQ = int(datalist[2])
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+"SYN-ACK")
        sock.sendto(pkt, addr)
        expected_seqn += 1
        # ACK
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        datalist = data.decode("utf-8").split(SEPARATOR)
        print(datalist)
        nseq = int(datalist[1])
        if (int(datalist[0]) and expected_seqn==nseq):
            ThreeWH = False
    expected_seqn = 0

while Conn:
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    print(datalist)
    if (int(datalist[1])==expected_seqn):
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(expected_seqn)+SEPARATOR+"ACK")
        file.write(datalist[2])
        expected_seqn = (expected_seqn + 1) % MAX_NSEQ

sock.close()
file.close()

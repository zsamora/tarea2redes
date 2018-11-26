import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8000
file = open("tarea2res.txt","w")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Message format = "ACK-BIT|||SEQUENCE-NUMBER|||PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
FIN_HEADER = "1"
FIN_FALSE = "0"
SEPARATOR = "|||"
data = ""
addr = ""
TIMEOUT = 2
MAX_RT = 10
TwoWH = False
ThreeWH = True
Close = True
Conn = True

# Variables
MAX_NSEQ = 0
expected_seqn = 0
transm = 0

sock.bind((UDP_IP, UDP_PORT))

# Two way handshake
while TwoWH:
    # SYN
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    # SYN-ACK
    nseq = int(datalist[1])
    if (expected_seqn == nseq):
        MAX_NSEQ = int(datalist[3]) + 1
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+FIN_FALSE+SEPARATOR+"SYN-ACK")
        sock.sendto(pkt, addr)
        TwoWH = False


# Three way handshake
while ThreeWH:
    # SYN
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    # SYN-ACK
    nseq = int(datalist[1])
    if (expected_seqn == nseq):
        MAX_NSEQ = int(datalist[3]) + 1
        pkt = str.encode(ACK_HEADER+SEPARATOR+str(nseq)+SEPARATOR+FIN_FALSE+SEPARATOR+"SYN-ACK")
        sock.sendto(pkt, addr)
        expected_seqn += 1
        # ACK
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        datalist = data.decode("utf-8").split(SEPARATOR)
        nseq = int(datalist[1])
        if (int(datalist[0]) and expected_seqn==nseq):
            ThreeWH = False
    expected_seqn = 0

while Conn:
    if transm > MAX_RT:
        print("Closed connection with client")
        sock.settimeout(None)
        Conn = False
        Close = False
        break
    sock.settimeout(TIMEOUT) # No se recibe mas informacion o se cayo el server
    try:
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        if (int(datalist[2])):
            sock.settimeout(None)
            Conn = False
        elif (int(datalist[1])==expected_seqn):
            pkt = str.encode(ACK_HEADER+SEPARATOR+str(expected_seqn)+SEPARATOR+FIN_FALSE+SEPARATOR+"ACK")
            sock.sendto(pkt, addr)
            file.write(datalist[3])
            expected_seqn = (expected_seqn + 1) % MAX_NSEQ
    except Exception as e:
        print(e)
        transm += 1
        break

# Close conection server
while Close:
    # ACK_SERVER
    pkt = str.encode(ACK_HEADER+SEPARATOR+str(expected_seqn)+SEPARATOR+FIN_HEADER+SEPARATOR+"ACK_SERVER")
    sock.sendto(pkt, addr)
    expected_seqn = (expected_seqn + 1) % MAX_NSEQ
    # FIN_SERVER
    pkt = str.encode(PKG_HEADER+SEPARATOR+str(expected_seqn)+SEPARATOR+FIN_HEADER+SEPARATOR+"FIN_SERVER")
    sock.sendto(pkt, addr)
    expected_seqn = (expected_seqn + 1) % MAX_NSEQ
    # ACK_CLIENT
    data, addr = sock.recvfrom(1024)
    datalist = data.decode("utf-8").split(SEPARATOR)
    if (int(datalist[0]) and int(datalist[2])):
        Close = False
        file.close()
        sock.close()
        break

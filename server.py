import socket
import sys

UDP_IP = "127.0.0.1"
UDP_PORT = 8000
file = open("tarea2res.txt","w")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Message format = "ACK-BIT|||SEQUENCE-NUMBER|||FIN-BIT|||PACKAGE"
ACK_HEADER = "1" # ACK=True/False
PKG_HEADER = "0"
FIN_HEADER = "1"
FIN_FALSE = "0"
SEPARATOR = "|||"
data = ""
addr = ""
TIMEOUT = 20
MAX_RT = 10
TwoWH = True#sys.argv[1]
ThreeWH = False#sys.argv[2]
Conn = True
Close = True

# Variables
MAX_NSEQ = 0
expected_seqn = 0
transm = 0

# Socket
sock.bind((UDP_IP, UDP_PORT))

# Two way handshake
while TwoWH:
    sock.settimeout(TIMEOUT) # MAX_RT * 2 seg (tiempo en que el cliente desiste)
    try:
        # SYN
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print (datalist)
        # SYN-ACK
        if (expected_seqn == int(datalist[1])):
            sock.settimeout(None)
            MAX_NSEQ = int(datalist[3]) + 1
            pkt = str.encode(ACK_HEADER+SEPARATOR+str(expected_seqn)+SEPARATOR+FIN_FALSE+SEPARATOR+"SYN-ACK")
            sock.sendto(pkt, addr)
            expected_seqn += 1
            transm = 0
            TwoWH = False
            print ("Conexion con el cliente establecida con exito")
    except Exception as e:
        print(e)
        print("Can't stablish connection with client")
        Conn = False
        Close = False
        file.close()
        sock.close()
        break

# Three way handshake
while ThreeWH:
    sock.settimeout(TIMEOUT) # MAX_RT * 2 seg (tiempo en que el cliente desiste)
    try:
        # SYN
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print (datalist)
        # SYN-ACK
        if (expected_seqn == int(datalist[1])):
            MAX_NSEQ = int(datalist[3]) + 1
            pkt = str.encode(ACK_HEADER+SEPARATOR+str(int(datalist[1]))+SEPARATOR+FIN_FALSE+SEPARATOR+"SYN-ACK")
            sock.sendto(pkt, addr)
            expected_seqn += 1
            # ACK
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            datalist = data.decode("utf-8").split(SEPARATOR)
            print (datalist)
            if (int(datalist[0]) and expected_seqn<=int(datalist[1])):
                sock.settimeout(None)
                ThreeWH = False
                expected_seqn += 1
                print ("Conexion con el cliente establecida con exito")
            else:
                expected_seqn = 0
    except Exception as e:
        print(e)
        print("Can't stablish connection with client")
        expected_seqn = 0
        Conn = False
        Close = False
        file.close()
        sock.close()
        break



while Conn:
    sock.settimeout(TIMEOUT) # No se recibe mas informacion o se cayo el server
    try:
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        if (int(datalist[2])):
            sock.settimeout(None)
            Conn = False
            print("Se cerrara la conexion")
        elif (int(datalist[1])==expected_seqn):
            print (datalist)
            pkt = str.encode(ACK_HEADER+SEPARATOR+str(expected_seqn)+SEPARATOR+FIN_FALSE+SEPARATOR+"ACK")
            sock.sendto(pkt, addr)
            file.write(datalist[3])
            expected_seqn = (expected_seqn + 1) % MAX_NSEQ
        else:
            pkt = str.encode(ACK_HEADER+SEPARATOR+str((expected_seqn-1)%MAX_NSEQ)+SEPARATOR+FIN_FALSE+SEPARATOR+"ACK")
            sock.sendto(pkt, addr)
    except Exception as e:
        print(e)
        print("Closed connection with client")
        sock.settimeout(None)
        Conn = False
        Close = False
        file.close()
        sock.close()
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
    sock.settimeout(TIMEOUT)
    try:
    # ACK_CLIENT
        data, addr = sock.recvfrom(1024)
        datalist = data.decode("utf-8").split(SEPARATOR)
        print(datalist)
        if (int(datalist[0]) and int(datalist[2])):
            sock.settimeout(None)
            Close = False
            file.close()
            sock.close()
            print("Conexion con el cliente cerrada con exito")
            break
    except Exception as e:
        print(e)
        print("Can't close connection with client correctly")
        Close = False
        file.close()
        sock.close()
        break

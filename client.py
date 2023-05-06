import segnali
import socket

while True:
    print("1: restart")
    print("2: stop engine")
    print("0: uscita")
    m = input("Inserisci menu: ")
    if m == "0":
        break;
    elif m == "2":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            c.connect((segnali.HOST, segnali.PORT))
            c.sendall(segnali.STOP_PS)
    elif m == "1":
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
            c.connect((segnali.HOST, segnali.PORT))
            c.sendall(segnali.RESTART)
            data = c.recv(1024)
            if data == segnali.OK:
                print("backup riattivato")
    else:
        print("Opzione non gestita")

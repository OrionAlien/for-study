import os
from os import *
from multiprocessing import *
from os.path import *
import signal
from socket import *
HOST = "127.0.0.1"
PORT = 8888
ADDR = (HOST,8888)
sockfd = socket()
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)

sockfd.bind(ADDR)
sockfd.listen(5)
def handle(c):
    sockfd.close()
    while True:
        data = c.recv(1024)
        if data:
            print(c.getpeername(),":",data.decode())
            c.send("ok".encode())
        else:
            c.close()
            os._exit(0)
            break


while True:
    try:
        connfd,addr = sockfd.accept()
        print("connect to %s %s"%addr)
        print(connfd.getpeername())
    except KeyboardInterrupt:
        os._exit(0)
    except Exception as i:
        print(i)
        pass

    p = Process(target=handle,args=(connfd,))
    p.daemon = True
    p.start()
    connfd.close()


import os
import socket
from threading import Thread
import sys
from Cliente import Client
from tkinter import Tk
import random


def send(host_to_connect,filename):
        print(host_to_connect)
        client_socket = socket.socket()  # instanciar
        client_socket.connect((host_to_connect, 2555 ))  # conectar ao nodo (oNode mais proximo)
        port = random.randint(4000, 5000)               # escolha da porta (reservou-se o intervalo 4000-5000)
        msg = f'{port}'
        print(msg)
        client_socket.send(msg.encode())                # envia a porta para o nodo em formato utf-8
        
        root = Tk()                     # instanciar a interface que vai mostrar a reprodução da stream
        # Create a new client
        os.environ.__setitem__('DISPLAY', ':0.0')
        content = "movie.Mjpeg"
        app = Client(root, host_to_connect, port, '5008', content)     # criar um worker para o cliente 
        app.master.title("RTPClient")	
        root.mainloop()



if __name__ == '__main__':
        host_to_connect = sys.argv[1]   # endereço do primeiro nodo ao qual se conecta
        filename = sys.argv[2]          # nome do video que pretende receber a stream
        Thread(target=send, args = (host_to_connect,filename)).start()
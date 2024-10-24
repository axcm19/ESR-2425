import os
import pickle
import socket
import subprocess
from threading import Thread
import sys
import time
from Cliente import Client
from tkinter import Tk
import random


def send(host_to_connect,filename):
        print(host_to_connect)
        client_socket = socket.socket()  # instanciar
        client_socket.connect((host_to_connect, 2555 ))  # conectar ao nodo (oNode mais proximo)
        port = random.randint(4000, 5000)               # escolha da porta (reservou-se o intervalo 4000-5000)
        msg = f'{port}'
        print(f"Connecting to POP in port = {msg}")
        client_socket.send(msg.encode())                # envia a porta para o nodo em formato utf-8
        
        root = Tk()                     # instanciar a interface que vai mostrar a reprodução da stream
        # Create a new client
        os.environ.__setitem__('DISPLAY', ':0.0')

        #content = "movie.Mjpeg"
        content = filename

        app = Client(root, host_to_connect, port, '5008', content)     # criar um worker para o cliente 
        app.master.title("RTPClient")	
        root.mainloop()



def checkLatencyWithPing(ip):
    # Executa o comando ping e captura a saída
    try:
        output = subprocess.check_output(["ping", "-c", "1", ip], universal_newlines=True)
        
        # Procura pelo tempo de resposta na saída
        for line in output.splitlines():
            if "time=" in line:
                time = line.split("time=")[1].split(" ")[0]
                return float(time)
            
    except subprocess.CalledProcessError:
        # Se o ping falhar
        print(f"Cant ping {ip}")
        return None



def loginSend(host_to_connect, filename):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_to_connect, 2666))  # Conectar ao servidor

    port_to_receive = f'{random.randint(6000, 7000)}' 
    print(f"Connecting to server {host_to_connect} in port = {port_to_receive}")
    client_socket.send(port_to_receive.encode())  # Enviar a porta para o servidor

    Thread(target=loginReceive, args=(filename,port_to_receive)).start()



def loginReceive(filename, port_to_receive):
    
    port =  int(port_to_receive)

    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.bind(('', port))  
    new_socket.listen(1)  # Aceita apenas uma conexão

    conn, address = new_socket.accept()  # Aceitar nova conexão

    poplist = conn.recv(1024)  # Recebe a lista de POPs

    popsParsed = []
    popsUnParsed = pickle.loads(poplist)  # Desserializa a lista de POPs

    for pop in popsUnParsed:
        popsParsed.append(pop)

    print(f"POPs list received: {popsParsed}")

    conn.close()

    # Escolhe um POP aleatório
    #random_index = random.randint(0, len(popsParsed) - 1)
    #mypop = popsParsed[random_index]


    # Escolhe um POP com base no tempo de resposta do ping
    times = {}

    for ip in popsParsed:
        time = checkLatencyWithPing(ip)

        if time is not None:
            times[ip] = time
            print(f"IP: {ip}, response time: {time} ms")

        else:
            print(f"IP: {ip}, did not respond")
    
    # Verifica qual IP tem o menor tempo
    mypop = min(times, key=times.get)
    
    print(f"Conectando ao POP em {mypop}")

    Thread(target=send, args=(mypop, filename)).start()




if __name__ == '__main__':

        #host_to_connect = sys.argv[1]   # endereço do primeiro nodo ao qual se conecta
        boot_ip = sys.argv[1]   # endereço do bootstraper que lhe vai dizer quem ão os POP

        filename = sys.argv[2]          # nome do video que pretende receber a stream
        #Thread(target=send, args = (host_to_connect,filename)).start()
        
        Thread(target=loginSend, args = (boot_ip, filename)).start()
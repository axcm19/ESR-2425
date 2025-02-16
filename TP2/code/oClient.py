import os
import pickle
import socket
import subprocess
from threading import Thread
import sys
#import time
from time import sleep
from Cliente import Client
from tkinter import Tk
import random



popToConect = "" # wich pop it will conect to based on the filename



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



def send(host_to_connect,filename):
        #print(host_to_connect)
        client_socket = socket.socket()  # instanciar
        client_socket.connect((host_to_connect, 2555 ))  # conectar ao nodo (oNode mais proximo)
        port = random.randint(4000, 5000)               # escolha da porta (reservou-se o intervalo 4000-5000)
        msg = f'{port}'
        print(f"Connecting to POP in port = {msg}")
        client_socket.send(msg.encode())                # envia a porta para o nodo em formato utf-8
        
        root = Tk()                     # instanciar a interface que vai mostrar a reprodução da stream
        # Create a new client
        os.environ.__setitem__('DISPLAY', ':0.0')

        content = filename

        app = Client(root, host_to_connect, port, '5008', content)     # criar um worker para o cliente 
        app.master.title("RTPClient")	
        root.mainloop()



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



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
        


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



def loginSend(host_to_connect, filename):

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host_to_connect, 2666))  # Connect to the server

        port_to_receive = random.randint(6000, 7000) 
        print(f"Connecting to server {host_to_connect} on port = {port_to_receive}")
        client_socket.send(str(port_to_receive).encode())  # Send port to server

        client_socket.close()  # Close the client socket after sending port
        Thread(target=loginReceive, args=(filename, port_to_receive)).start()
    
    except Exception as e:
        print(f"Error in loginSend: {e}")



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



def loginReceive(filename, port_to_receive):

    global popToConect
    
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
    
    conn.close()

    print(f"POPs list received: {popsParsed}")


    if(popToConect == ""):
        print("Choosing a pop with ping")

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
        popToConect = mypop 

    print(f"Connecting to POP {popToConect}")

    Thread(target=send, args=(popToConect, filename)).start()



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



if __name__ == '__main__':

        boot_ip = sys.argv[1]   # endereço do bootstraper que lhe vai dizer quem ão os POP

        filename = sys.argv[2]          # nome do video que pretende receber a stream
        
        Thread(target=loginSend, args = (boot_ip, filename)).start()
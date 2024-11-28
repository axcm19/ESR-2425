import socket
import subprocess
from threading import Thread
import json
import sys
import pickle
import b_database
from time import sleep
import time
import os
import re
import cv2
import traceback



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


#leitura do ficheiro de configuração da topologia
def readConfigFile(topo):
    print('reading config file ..')
    with open(topo) as json_file:
        data = json.load(json_file)
    return data



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



#funçaõ responsável por establecer uma conexão
def initializeConnectionsWorker(conn,address,database):
    
        database.addPeerConnected()
        data = conn.recv(1024).decode()

        if data:
            neighboursList = []
            #getting neighbours list
            for key,value in database.getTopo().items():
            
                if address[0] in value['names']:
                    print('sending neighbours to ' + key)
                    neighboursList = value['neighbours']

            #verifica se todos os nodos já se encontram conectados   
            print(f'PeersConnected = {database.getPeersConnected()}')
            print(f'NumberPeer = {database.getNumberPeer()}') 
            while(database.getPeersConnected() < database.getNumberPeer()): 
                pass
    
        conn.send(pickle.dumps(neighboursList))  # send data to the client
        print('finished sending neighbours to everyone')
        conn.close()  # close the connection



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



#função responsável pelo establecimento de todas conexões
def initializeConnections(database):
    
    print('Inicializing Connections')
    # get the hostname
    port = 1111
    #read config file
    nodesNumber = len(database.getTopo().keys()) - 1
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))  
    server_socket.listen(nodesNumber) 
    for i in range(nodesNumber):
        conn, address = server_socket.accept()  # accept new connection
        Thread(target=initializeConnectionsWorker, args = (conn,address,database)).start()




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
    


#função responsável por monitorizar a rede overlay
def sendStatusServerNetwork(database):
    
    
    myname = socket.gethostname()
    neighbours = database.getTopo()[myname]['neighbours']
    i = 0
    
    while True:

        print('sending status')
        for neighbour in neighbours:
            connected = False
            while connected == False: 
                try:
                    status_socket = socket.socket()  # instantiate
                    status_socket.connect((neighbour, 4444))  # connect to the server
                    message = f'servername:{myname} time:{time.time()} jumps:{1} visited:'
                    status_socket.send(message.encode())  # send message
                    connected = True
                    print('connected')
                    i = i + 1
                    
                except:
                    #print('all my neighbours are offline')
                    pass
        sleep(30)




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# receber um pedido de stream pelo worker e tratar o envio
def receiveStreamRequestWorker(filename,address,database,udpSocket):
      
    i = 0

    while database.getStreamState(filename) == 'activated': #verificar se a stream ainda se encontra ativada

        try:
            file = cv2.VideoCapture(filename) #open file
        except:
            print("Error opening file!")
            raise IOError
        
        success, data = file.read()
        print(f"\nbegin streaming {filename}")
        
        while success:

            #print(i)
            frame = cv2.imencode('.jpg', data, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tobytes() # leitura de uma frame
            udpSocket.sendto(frame, address) #envio de cada frame
            if database.getStreamState(filename) != 'activated' : break
            i += 1
            success, data = file.read()
            sleep(0.05)
            


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

            

#função responsável por atender a pedidos de stream
def receiveStreamRequest(database):

        udpSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udpSocket.bind(('', 6666))

        while(True):

                msg , address = udpSocket.recvfrom(1024) #receber pedido

                request = msg.decode()

                splitted = re.split(' ',request)

                filename = splitted[0] # nome do ficheiro de pedido

                teardown = splitted[1]

                if teardown != 'TEARDOWN':
                    database.addStream(filename)
                    Thread(target=receiveStreamRequestWorker, args = (filename,address,database,udpSocket)).start()
                else:
                    database.changeStreamState(filename)



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# Thread que vai receber as conexões dos clientes, por cada uma delas, vai criar uma thread para tratar da autenticação do cliente
def clientConnectionsLoginReceive(database):

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', 2666))
        server_socket.listen(socket.SOMAXCONN)  # determinar automaticamente um valor máximo razoável de connections

        while True:
            conn, address = server_socket.accept()
            port = conn.recv(1024).decode()
            print(f"Received port {port} from {address[0]}")
            conn.close()

            # Start a thread to handle each client connection with the provided port and database
            Thread(target=clientConnectionsLoginSend, args=(address[0], int(port), database)).start()
    
    except Exception as e:
        print(f"Error in clientConnectionsLoginReceive: {e}")
    finally:
        server_socket.close()



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# Thread que vai responder as conexões dos clientes, por cada uma delas
def clientConnectionsLoginSend(client_to_respond, port_to_receive, database):

        
    for attempt in range(3):
        port = int(port_to_receive)
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# Set up the client socket
            client_socket.connect((client_to_respond, port))  # Connect to the specified client
            print(f"Connected to client at {client_to_respond}:{port}")
            break
        except ConnectionRefusedError:
            print(f"Attempt {attempt + 1}: Connection refused, retrying...")
            time.sleep(1)
    else:
        print("Failed to connect to client after multiple attempts.")
        return
    
    # Retrieve all nodes from the database
    allNodes = database.getTopo()
    popsList = []

    # Collect all points of presence (POP) IPs from the nodes, excluding server nodes
    for n in allNodes:
        if "s" not in n:  # Assuming "s" denotes server nodes
            if allNodes[n].get('pop'):  # Check if 'pop' key exists and is not empty
                popsList.extend(allNodes[n]['pop'])  # Add all IPs in 'pop' to popsList

    print(f"List of points of presence available = {popsList}")

    # Send the list of POPs to the client
    client_socket.send(pickle.dumps(popsList))

    print('Finished sending POPs to client')
    
    client_socket.close()



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#       

                   

#if __name__ == '__main__':
def run_server(topologia, opt_boot):

    database = b_database.b_database()
    database.setTopo(readConfigFile(topologia))
    option = int(opt_boot)

    #database.setTopo(readConfigFile(sys.argv[1]))
    #option = int(sys.argv[2])

    if(option==1):      # valor 1 indica que é o bootstrapper, caso o valor seja 0 é um servidor normal
        Thread(target=initializeConnections, args = (database,)).start()
        Thread(target=clientConnectionsLoginReceive, args = (database,)).start()

    Thread(target=sendStatusServerNetwork, args = (database,)).start()
    Thread(target=receiveStreamRequest, args = (database,)).start()
    

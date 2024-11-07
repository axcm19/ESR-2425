import socket
import threading
from threading import Thread
import json
import sys
import pickle
import ServerWorker
import b_database
from time import sleep



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# ler o ficheiro json que corresponde à configuração da topologia (vizinhos e interfaces por nodo e servidor)
def readConfigFile(topo):
    print('reading config file ..')
    with open(topo) as json_file:
        data = json.load(json_file)
    return data



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# começar o funcionamento do servidor
def server():
	try:
		SERVER_PORT = 5555
	except:
		print("[Usage: Server.py Server_port]\n")
	rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	rtspSocket.bind(('', SERVER_PORT))
	rtspSocket.listen(5)    
	# receber a informação do cliente (address,port) através de uma RTSP/TCP session
	while True:
		clientInfo = {}
		clientInfo['rtspSocket'] = rtspSocket.accept()
		ServerWorker(clientInfo).run()		



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# worker que lê a topologia e permite aos nodos conhecerem a sua vizinhança
def initializeConnectionsWorker(conn,address,dicTopo,database):
    
        database.addPeerConnected()
        data = conn.recv(1024).decode()
        if data:
            neighboursList = []
            #obter a lista de vizinhos
            for key,value in dicTopo.items():
            
                if address[0] in value['names']:
                    print('sendig neighbours to ' + key)
                    neighboursList = value['neighbours']
            #garantir o nº mínimo de peers conectados (pelo menos 2)
            while(b_database.getPeersConnected() < 2):
                print('Not enough peers')
                sleep(2)
    
        conn.send(pickle.dumps(neighboursList))  # enviar a lista de vizinhos ao nodo num objeto bytes
        print('Finished sending neighbours...')
        conn.close()  # fechar a conexão



#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



# leitura da topologia e inicialização das conexões, que aceita as conexões com cada nodo e chama o respectivo worker para cada um
def initializeConnections(topo, database):
    
    print('Inicializing Connections')
    # get the hostname
    port = 1111
    #read config file
    dicTopo = readConfigFile(topo)  # ler o ficheiro json que corresponde à configuração da topologia
    nodesNumber = len(dicTopo)  # obter o nº de nodos (servidores + oNodes)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))  
    server_socket.listen(nodesNumber)   # ficar à escuta de novas conexões, limitando o nodo a aceitar apenas o nº de conexões correspondente ao nº de nodos (garantir o nº exato de conexões)
    for i in range(nodesNumber):
        conn, address = server_socket.accept()  # aceitar nova conexão
        Thread(target=initializeConnectionsWorker, args = (conn,address,dicTopo,database)).start()  # começar um novo worker para dar a conhecer a vizinhança
    


#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



if __name__ == '__main__':

    b_database = b_database.b_database()
    topo = sys.argv[1]

    Thread(target=initializeConnections, args = (topo,b_database)).start()
    Thread(target=server, args = ()).start()


    
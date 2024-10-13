import socket
import traceback
from time import sleep


class database:
    neighbours : list #lista de neighbours
    serversNeighbours : list #list of servers in neighbourhood
    serverStatus : dict #metrics of server connection in neighbourhood
    streamsDict : dict #dict of streams in the node
    routeStreamDict : dict #metrics of streams in neighbourhood


    def __init__(self):
        self.neighbours = []
        self.serverStatus = {}
        self.streamsDict = {}
        self.routeStreamDict = {}
        self.metricsInNeighbourhood = {}

    #adicionar a lista de vizinhos que são servidores
    def putServersNeighbours(self,neighbours):
        self.serversNeighbours = neighbours

    def getServersNeighbours(self):
        return self.neighbours

    #adicionar a lista de vizinhos que não nodos
    def putNeighbours(self,neighbours):
        self.neighbours = neighbours

    # obter os vizinhos
    def getNeighbours(self):
        return self.neighbours

    # adicionar uma conexao ao STATUS do servidor (monitorização da rede)
    def putConnectionServerStatus(self,neighbour,connection):

        if neighbour in  self.serverStatus.keys():
            if self.serverStatus[neighbour]['servername'] != connection['servername']:
                if abs(self.serverStatus[neighbour]['timestamp'] - connection['timestamp']) < 0.1 * min(self.serverStatus[neighbour]['timestamp'],connection['timestamp']):
                        if (self.serverStatus[neighbour]['jumps'] > connection['jumps']):
                            self.serverStatus[neighbour] = connection          
                elif self.serverStatus[neighbour]['timestamp'] > connection['timestamp']:
                    self.serverStatus[neighbour] = connection 
        else:
            self.serverStatus[neighbour] = connection

    def getConnectionServerStatus(self,neighbour):
        return self.serverStatus[neighbour]

    # obter uma stream
    def getStream(self,streamName):
        if(streamName in self.streamsDict.keys()):
            if self.streamsDict[streamName]['state'] == 'activated': return self.streamsDict[streamName]
            else: return False
        else:
            return False

    # obter o estado de uma stream        
    def getStreamState(self,streamName):
            if(streamName in self.streamsDict.keys()):
                return self.streamsDict[streamName]['state']
            else: return False

    # alterar o estado de uma stream
    def changeStreamState(self,streamName,state):
            if(streamName in self.streamsDict.keys()):
                self.streamsDict[streamName]['state'] = state
            else: return False
    
    # colocar uma stream como vazia (reiniciar para que volte ao ponto zero)
    def putStreamEmpty(self,streamName):
        dic = {}
        dic['state'] = 'activated'
        dic['receivers'] = []
        dic['clients'] = {}
        self.streamsDict[streamName] = dic

    # adicionar um receptor à stream (verifica-se se está ativa, sendo portanto possível adicionar) (receiver é um nodo)
    def addStreamReceiver(self,streamName,ip):
        try:
            if self.streamsDict[streamName]['state'] == 'activated':
                self.streamsDict[streamName]['receivers'].append(ip)
            else : return False
        except Exception: 
            return False

    # remover um receptor da stream (receiver é um nodo)
    def removeStreamReceiver(self,streamName,ip):
        try:
            self.streamsDict[streamName]['receivers'].remove(ip)

            if len(self.streamsDict[streamName]['receivers']) == 0 and len(self.streamsDict[streamName]['clients'].keys()) == 0:
                self.streamsDict[streamName]['state'] = 'disabled'
                print(self.streamsDict[streamName]['state'])

        except Exception: 
            return False
    
    # obter os receptores por stream (receiver é um nodo)
    def getStreamReceivers(self,streamName):
        try:
            return self.streamsDict[streamName]['receivers']
            
        except Exception: 
            return False

    # adicionar um cliente para uma stream
    def addStreamClient(self,streamName,ip):
        try:
            if self.streamsDict[streamName]['state'] == 'activated':
                self.streamsDict[streamName]['clients'][ip] = []
            else: return False
        except :
            return False

    # remover um cliente de uma stream
    def removeStreamClient(self,streamName,ip):
        try:
            self.streamsDict[streamName]['clients'].pop(ip, None)
            if len(self.streamsDict[streamName]['receivers']) == 0 and len(self.streamsDict[streamName]['clients'].keys()) == 0:
                self.streamsDict[streamName]['state'] = 'disabled'
                print(self.streamsDict[streamName]['state'])
            print('poped')
        except :
            return False

    # obter os clientes por stream
    def getStreamClients(self,streamName):
        return self.streamsDict[streamName]['clients'].keys()

    # adicionar um pacote da stream para o cliente
    def putStreamPacket(self,streamName,ip,packet):
        
        try:
            self.streamsDict[streamName]['clients'][ip].append(packet)
        except:
            pass
        

    def popStreamPacket(self,streamName,ip):
        try:
                return self.streamsDict[streamName]['clients'][ip].pop(0)
        except Exception:
            # traceback.print_exc()
            return None
         
    # obter as melhores métricas para o STATUS (monitorização da rede), sendo o 1º caso de decisao o timestamp, e o 2º caso de decisao o numero de saltos
    def getBestMetricsServerStatus(self,comeFrom):
        
            timestamp = 9999999999
            neighbourAux = ''
            jumps = 9999999999
            for neighbour in self.serverStatus.keys():
                if(neighbour not in comeFrom):
                    print(self.serverStatus[neighbour]['timestamp'] , timestamp)
                    # em caso de a variacao ser superior a 10% verifica-se o nº de saltos
                    if abs(self.serverStatus[neighbour]['timestamp'] - timestamp) < 0.1 * min(self.serverStatus[neighbour]['timestamp'],timestamp):
                        if (self.serverStatus[neighbour]['jumps'] < jumps):
                            neighbourAux = neighbour
                            timestamp = self.serverStatus[neighbour]['timestamp']
                            jumps = self.serverStatus[neighbour]['jumps']    
                    elif self.serverStatus[neighbour]['timestamp'] < timestamp:
                        neighbourAux = neighbour
                        timestamp = self.serverStatus[neighbour]['timestamp'] 
                        jumps = self.serverStatus[neighbour]['jumps']
                
                
                    print(neighbour,neighbourAux)
                
            return neighbourAux
    
   
    # adicionar a rota para uma stream
    def putRouteStreamDict(self,filename,neighbour,metrics):
            if filename in self.routeStreamDict.keys():
                self.routeStreamDict[filename][neighbour] = metrics
            else :
                self.routeStreamDict[filename] = {}
                self.routeStreamDict[filename][neighbour] = metrics


    # calcular as melhores metricas para uma stream (1º timestamp, 2º jumps)
    def getBestMetricsRouteStreamDict(self,filename):
            dict =  self.routeStreamDict[filename]

            timestamp = 9999999999
            neighbourAux = ''
            jumps = 9999999999
            for neighbour in dict.keys():
                print(dict[neighbour]['timestamp'] , timestamp)
                # em caso de a variacao ser superior a 10% verifica-se o nº de saltos
                if (abs(dict[neighbour]['timestamp'] - timestamp) < 0.1 * timestamp):
                    if dict[neighbour]['jumps'] < jumps:
                        timestamp = dict[neighbour]['timestamp']
                        neighbourAux = neighbour
                        jumps = dict[neighbour]['jumps']
                elif dict[neighbour]['timestamp'] < timestamp:
                    neighbourAux = neighbour
                    timestamp = dict[neighbour]['timestamp']
                    jumps = dict[neighbour]['jumps']
                
                print(neighbour,neighbourAux)
            
            return neighbourAux
    

    def getNumberOfRouteStream(self,filename):
        if filename in self.routeStreamDict.keys():
            return len(self.routeStreamDict[filename].keys())
        else: return 0
                
            

    def getMetricsRouteStreamDict(self,filename, neighbour):
            return self.routeStreamDict[filename][neighbour]

            





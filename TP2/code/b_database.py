class b_database:
    peersConnected : int    # número de peers conectados
    topo : dict        # topologia lida a partir de um ficheiro json para um dicionário em que na chave contém o nome do peer e no valor contém os vizinhos e as interfaces por peer
    file : list         # ficheiro a ser transmitido
    streams : dict      # dicionário que contém o estado e os receptores por stream

    def __init__(self):
        self.peersConnected = 0
        self.file = []
        self.streams = {}

    #obter o nº de peers conectados
    def getPeersConnected(self):
        return self.peersConnected
    
    #incrementar o nº de peers conectados
    def addPeerConnected(self):
        self.peersConnected = self.peersConnected + 1

    #definir a topologia
    def setTopo(self,topo):
        self.topo =  topo
    
    #obter a topologia (dicionário)
    def getTopo(self):
        return self.topo

    #definir o ficheiro a ser transmitido
    def setFile(self, file):
        self.file = file

    #obter o ficheiro a ser transmitido
    def getFile(self):
        return self.file
    
    #obter o nº de peers
    def getNumberPeer(self):
        r=0
        for key in self.topo:
            if("s1" not in key):
                r = r + 1
        return r

    #adicionar uma nova stream às streams de um ficheiro (estado é definido como ativo e é inicializado sem receptores)
    def addStream(self,filename):
        dic = {}
        dic['state'] = 'activated'
        dic['receivers'] = []
        self.streams[filename] = dic

    #obter o estado de uma stream
    def getStreamState(self,filename):
        return self.streams[filename]['state']

    #alterar o estado de uma stream para desativado
    def changeStreamState(self,filename):
        self.streams[filename]['state'] = 'disabled'
        print('disabled')

    
    


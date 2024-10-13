import netifaces

def getMyNames():
        mynames = []
        index = 0
        for interface in netifaces.interfaces():
                if(index != 0):
                        for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                                    mynames.append(link['addr'])
                index = index + 1
        return mynames


 
#get my names
mynames = getMyNames()

visited = []
#construct visited list with all node names
newvisited = ""
index = 0
if len(visited) != 0:
    for vis in visited:
        if(index == 0):
                newvisited = newvisited + vis
        else:
                newvisited = newvisited + ',' + vis
        index = index + 1
    for name in mynames:
            newvisited = newvisited + ',' + name
                        
else:
        for name in mynames:
                if index == 0 :newvisited = newvisited + name
                else: newvisited = newvisited + ',' + name
                index = index + 1

print(newvisited)
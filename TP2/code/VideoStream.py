
from time import sleep

class VideoStream:
	def __init__(self, filename, database, clientIp):
		self.filename = filename
		self.database = database
		self.clientIp = clientIp
		self.frameNum = 0
		
		vartry = False
		while vartry == False:
			vartry = database.addStreamClient(filename,clientIp)
		
			

	def run(self):
		pass
	
	def nextFrame(self):
	
		
		nextframe = self.database.popStreamPacket(self.filename,self.clientIp)
		self.frameNum += 1
		
		return nextframe

		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	

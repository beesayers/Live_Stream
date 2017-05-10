import sys
import threading
import socket
import random
import pickle
import time
import retrieve_pckge_vid
import imageio

class Server:
	def __init__(self, theClient):
		self.clientInfo = theClient
		self.clientIP = self.clientInfo[1]
		self.currentstate = "INITIAL"
		self.rtpSeqNo = 0
		self.firstLaunch = True
		self.liveRecording = retrieve_pckge_vid.myPiStream()
		threading.Thread(target = self.receiveRTSP).start()

	# 50 minutes
	def receiveRTSP(self):
		self.rtspSocket = self.clientInfo[0][0]
		print("Waiting for RTSP command.")
		while True:
			try:
				rawdata = self.rtspSocket.recv(256)
				if rawdata:
					self.processRTSP(rawdata)
			except OSError:
				sys.exit(1)

	# 2 hours 2 minutes
	def processRTSP(self, rawdata):
		data = self.unpickleIt(rawdata)
		self.clientCommand = data[0]
		self.rtspSeqNo = data[1]

		if self.currentstate == "INITIAL" and self.clientCommand == "SETUP":
			print("Received Setup Request from Client...")
			self.currentstate = 'READY'
			self.rtpPort = int(data[2])
			self.sessionID = random.randint(10000, 99999)
			self.sendRTSP('200')

		elif self.currentstate == "READY" and self.clientCommand == "PLAY":
			print("Received Play Request from Client...")
			self.currentstate = 'PLAYING'
			self.sendRTSP('200')

			# launch recorder
			if self.firstLaunch:
				threadRecording = threading.Thread(target = self.liveRecording.startUp(self.firstLaunch))
				threadRecording.start()
				self.firstLaunch = False

			else:
				print("Loading... please wait.")
				self.liveRecording.clientCmd("c")

			# Create RTP socket
			self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			# Create new thread and start sending RTP packets
			threading.Thread(target = self.sendRTP).start()

		elif self.currentstate == 'PLAYING' and self.clientCommand == 'PAUSE':
			print("Received Pause Request from Client...")
			self.currentstate = 'READY'

			# Tell recorder to stop recording
			self.liveRecording.stopRecording(True)
			self.sendRTSP('200')

		elif self.clientCommand == 'TEARDOWN':
			print("Received Teardown Request from Client...")
			self.liveRecording.clientCmd("k")
			self.sendRTSP('200')
			self.rtspSocket.close()
			self.rtpSocket.close()
			return True

	# 11 minutes
	def sendRTSP(self, statuscode):
		if statuscode == '200':
			print("Session: %d | Sequence: %d | Status Code: %s\n" %(self.sessionID, self.rtspSeqNo, statuscode))
			packet = self.pickleIt([statuscode, self.rtspSeqNo, self.sessionID])
			self.rtspSocket.send(packet)
		else:
			print("Status Code ERROR")

	# 7 hours 13 minutes
	def sendRTP(self):
		print("Preparing to send RTP packets...")
		ready = False
		while not ready:
			try:
				tryToOpenFirstFile = open('Master_Snaps/0.jpg')
				print("Ready!")
				ready = True
			except FileNotFoundError:
				pass
		# Loop through video clips
		count = 0
		folder = 'Master_Snaps/'
		while True:
			fail = False
			if self.currentstate != 'PLAYING':
				break
			elif self.clientCommand == 'TEARDOWN':
				break
			else:
				self.rtpSeqNo += 1
				fileName = folder + str(count) + '.jpg'
				print("Sending file number: " + str(count))
				try:
					with open(fileName, 'rb') as reader:
						packet = [26, self.rtpSeqNo, str(time.time()), reader.read()] # had reader.read()
						self.rtpSocket.sendto(self.pickleIt(packet), (self.clientIP, int(self.rtpPort)))
				except FileNotFoundError:
					print("server going too fast")
					fail = True
				if count is 9999:
					count = 0
				elif not fail:
					count += 1

	def pickleIt(self, packet):
		return pickle.dumps(packet)

	def unpickleIt(self, packet):
		return pickle.loads(packet)
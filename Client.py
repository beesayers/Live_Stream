# Brandon Sayers
# Rocco Haro

from tkinter import *
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
import sys
import socket
import threading
import os
import traceback
import pickle
import time
import imageio
import numpy as np

class Client:
	# Initialize our client
	# root: GUI object
	# serverAddress: IP address for server
	# serverPort: Port number for server
	# rtpPort: Port number for RTSP
	def __init__(self, root, serverAddress, serverPort, rtpPort):
		self.window = root
		self.buildWindow()

		self.lastcommand = ''
		self.currentstate = 'INITIAL'
		self.rtspSeqNo = 0
		self.rtpSeqNo = 0
		self.droppedFrames = 0
		self.sessionID = 0
		self.serverAddress = serverAddress
		self.serverPort = serverPort
		self.rtpPort = rtpPort

		self.establishRTSPConnect()

	# 33 minutes
	# Populate our window with actionable buttons and our "video".
	# self.setup: Changes state to READY.
	# self.play: Changes state to PLAYING. Begin receiving stream.
	# self.pause: Changes state to READY. Stop receiving stream.
	# self.teardown: Terminates the client.
	def buildWindow(self):
		self.window.protocol("WM_DELETE_WINDOW", self.manualExit)

		self.setup = Button(self.window, width = 12, padx = 2, pady = 2)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupPlayer
		self.setup.grid(row = 1, column = 0, padx = 2, pady = 2)

		self.play = Button(self.window, width = 12, padx = 2, pady = 2)
		self.play["text"] = "Play"
		self.play["command"] = self.playPlayer
		self.play.grid(row = 1, column = 1, padx = 2, pady = 2)

		self.pause = Button(self.window, width = 12, padx = 2, pady = 2)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pausePlayer
		self.pause.grid(row = 1, column = 2, padx = 2, pady = 2)

		self.teardown = Button(self.window, width = 12, padx = 2, pady = 2)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] = self.teardownPlayer
		self.teardown.grid(row = 1, column = 3, padx = 2, pady = 2)

		self.picture = Label(self.window, height = 30)
		self.picture.grid(row = 0, column=0, columnspan=4, padx=10, pady=10)

	# 4 minutes
	# Handler for when the window is abruptly exited.
	def manualExit(self):
		if messagebox.askokcancel("Exit Livestream" ,"Are you sure you wish to exit?"):
			self.teardownPlayer()

	# 4 minutes
	# Setup button handler.
	def setupPlayer(self):
		if self.currentstate == 'INITIAL':
			self.sendRTSP('SETUP')

	# 13 minutes
	# Play button handler.
	# Starts receive video data thread.
	def playPlayer(self):
		if self.currentstate == 'READY':
			threading.Thread(target = self.receiveRTP).start()
			self.videoThread = threading.Event()
			self.videoThread.clear()
			self.sendRTSP('PLAY')

	# 3 minutes
	# Pause button handler.
	def pausePlayer(self):
		if self.currentstate == 'PLAYING':
			self.sendRTSP('PAUSE')

	# 15 minutes
	# Teardown button/Exit handler.
	def teardownPlayer(self):
		self.sendRTSP('TEARDOWN')
		self.window.destroy()
		sys.exit(0)

	# 6 minutes
	# Connect rtspSocket to server.
	def establishRTSPConnect(self):
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddress, self.serverPort))
		except:
			messagebox.showwarning('Connection Unsuccessful', 'Connection to %s failed.' %self.serverAddress)

	# 44 minutes
	# Process button click and send RTSP packet with the command and sequence number.
	def sendRTSP(self, command):
		# Change states from INITIAL to READY.
		# Start receiving data from RTSP socket.
		if self.currentstate == 'INITIAL' and command == 'SETUP':
			print("Sending Setup Request to Server.........")

			threading.Thread(target = self.receiveRTSP).start()
			self.rtspSeqNo += 1
			packet = ['SETUP', self.rtspSeqNo, self.rtpPort]
			self.rtspSocket.send(self.pickleIt(packet))
			self.lastcommand = 'SETUP'

		# Change states from READY to PLAYING.
		elif self.currentstate == 'READY' and command == 'PLAY':
			print("Sending Play Request to Server.........")

			self.rtspSeqNo += 1
			packet = ['PLAY', self.rtspSeqNo]
			self.rtspSocket.send(self.pickleIt(packet))
			self.lastcommand = 'PLAY'

		# Change states from PLAYING to READY.
		elif self.currentstate == 'PLAYING' and command == 'PAUSE':
			print("Sending Pause Request to Server.........")

			self.rtspSeqNo += 1
			packet = ['PAUSE', self.rtspSeqNo]
			self.rtspSocket.send(self.pickleIt(packet))
			self.lastcommand = 'PAUSE'

		# If not in INITIAL state, change state to TEARDOWN.
		elif self.currentstate != 'INITIAL' and command == 'TEARDOWN':
			print("Sending Teardown Request to Server.........")

			self.rtspSeqNo += 1
			packet = ['TEARDOWN', self.rtspSeqNo]
			self.rtspSocket.send(self.pickleIt(packet))
			self.lastcommand = 'TEARDOWN'

	# 22 minutes
	def receiveRTSP(self):
		while True:
			rawdata = self.rtspSocket.recv(1024)

			if rawdata:
				self.processRTSP(rawdata)

			if self.lastcommand == 'TEARDOWN':
				self.rtspSocket.shutdown(socket.SHUT_RDWR)
				self.rtspSocket.close()
				break

	# 51 minutes
	def processRTSP(self, rawdata):
		data = self.unpickleIt(rawdata)
		print("Here is our data:")
		print(data)
		code = int(data[0])
		rtspSeqNo = data[1]
		sessionID = data[2]

		if rtspSeqNo == self.rtspSeqNo:
			if self.sessionID == 0:
				self.sessionID = sessionID

			if sessionID == self.sessionID and code == 200:
				if self.lastcommand == 'SETUP':
					print("RTP connection setup...\n")
					self.establishRTPConnect()
					self.currentstate = 'READY'

				elif self.lastcommand == 'PLAY':
					print("Loading video...\n")
					self.currentstate = 'PLAYING'

				# RTP-Receive thread stops and new thread will be created when client selects Play.
				elif self.lastcommand == 'PAUSE':
					print("Video was paused...\n")
					self.currentstate = 'READY'
					self.videoThread.set()

				elif self.lastcommand == 'TEARDOWN':
					print("Disconnecting stream...\n")
					self.currentstate = 'TEARDOWN'

	# 31 minutes
	# Create a new RTP Socket.
	# Bind the socket to server's RTP port.
	def establishRTPConnect(self):
		try:
			self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.rtpSocket.bind(('',self.rtpPort))
			self.rtpSocket.settimeout(3)
		except:
			messagebox.showwarning('Connection Unsuccessful', 'Connection to %s failed.' %self.serverAddress)

	# 1 hour 12 minutes
	def receiveRTP(self):
		count = 0
		while True:
			try:
				rawdata, address = self.rtpSocket.recvfrom(25000)
				if rawdata:
					self.processRTP(rawdata, count)
					count+=1
			except:
				if self.currentstate == "PLAYING":
					print("Loading...")
				else:
					print("Not Receiving Data...")
				if self.videoThread.isSet():
					break
				elif self.lastcommand == 'TEARDOWN':
					self.rtpSocket.close()
					break

	# 3 hours 15 minutes
	def processRTP(self, rawdata, pos):
		data = self.unpickleIt(rawdata)
		self.rtpSeqNo += 1

		payloadtype = data[0]
		rtpSeqNo = data[1]
		timestamp = data[2]
		videodata = data[3]
		print("Received RTP Data seq:" + str(rtpSeqNo))
		filePath = 'received/temp'+str(pos)+'.jpg'
		videofile = open(filePath, 'wb')
		videofile.write(videodata)
		videofile.close()

		videoreader = Image.open(filePath)
		if self.rtpSeqNo != rtpSeqNo:
			self.droppedFrames += (rtpSeqNo - self.rtpSeqNo)
			self.rtpSeqNo = rtpSeqNo
			print("!"*30 + "PACKET LOSS" + "!"*30)
		self.Player(videoreader)

	# 41 minutes
	def Player(self, videoreader):
		frame = ImageTk.PhotoImage(videoreader)
		self.picture.configure(image = frame, height=400)
		self.picture.image = frame

	def pickleIt(self, packet):
		return pickle.dumps(packet)

	def unpickleIt(self, packet):
		return pickle.loads(packet)
# Brandon Sayers
# Rocco Haro

from Client import Client

from tkinter import *
import sys

try:
	serverAddress = sys.argv[1]
	serverPort = int(sys.argv[2])
	rtpPort = int(sys.argv[3])
except:
	print("Please enter in this format:")
	print("python3 ClientLauncher.py 'Server Address' 'Host Port' 'RTP Port'")

root = Tk()
videoStream = Client(root, serverAddress, serverPort, rtpPort)
videoStream.window.title("Live Stream")
root.mainloop()
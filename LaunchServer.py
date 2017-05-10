# Brandon Sayers
# Rocco Haro
from Server import Server
import sys
import socket

# 5:41
try:
	port = sys.argv[1]
except:
	print("LaunchServer required format:")
	print("python3 LaunchServer.py 'Host Port'\n")

rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rtspSocket.bind(('', int(port)))
rtspSocket.listen(10)

# The accept function returns [socket ID, [client IP, integer]]
# theClient {socket, clientIP}
while True:
	try:
		theClient = rtspSocket.accept()
		clientInfo = [theClient, theClient[1][0]]
		kill = Server(clientInfo)
		if kill:
			sys.exit(0)
	except (KeyboardInterrupt, SystemExit):
		sys.exit()

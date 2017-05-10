## Live-Stream using RTSP/RTP Protocols

#### External Libraries
---
- imageio
- pygame for python3
- tkinter
- PIL
- numpy
- pickle

#### Setup and Install Libraries
---
- sudo -H pip3 install imageio
- sudo pip3 install setuptools

#### Objective
---
Utilize RTSP protocol to send requests from client to server. Utilize RTP to transfer data for live-stream from server to client. Create a videoplayer-esque GUI for user to send requests and display live-stream video.

#### Methods
---
1. Server and client establish TCP connection for RTSP protocol.
2. Client sends RTSP requests:
	- Setup: Required before any other actions.
	- Play: Begin streaming session using RTP protocol.
	- Pause: Halt server-side data transfer.
	- Teardown: Terminate client-side application and close connection gracefully.
3. After setup request is sent to the server, the client may begin the live-stream, pause the live-stream, teardown the connection.

#### Usage
---
Client side - To run, python3 LaunchClient.py <IP address> <RTSP Port> <RTP Port>

Server side - To run, python3 LaunchServer.py <RTSP Port>

#### Protocols and Transport Headers
---
RTSP - 	Client -> Server {command, RTSP seq num}

	Server -> Client {RTSP seq num, Session ID}
	
RTP  - 	Server -> Client {fileType code, RTP seq num, timestamp, payload}

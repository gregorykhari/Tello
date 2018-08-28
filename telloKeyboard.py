import threading 
import socket
import sys
import time
import msvcrt
 
host = ''
port = 9000
locaddr = (host,port) 

msg_decoder={'t':'takeoff','y':'land','u':'end','w':'up 20','s':'down 20','a':'ccw 20','d':'cw 20','i':'forward 20','k':'back 20','j':'left 20','l':'right 20'}

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

def recv():
	count = 0
	
	while True: 
		try:
			data, server = sock.recvfrom(1518)
			print(data.decode(encoding="utf-8"))
		except Exception:
			print ('\nExit . . .\n')
			break
			
#recvThread create
recvThread = threading.Thread(target=recv)
recvThread.start()

# Send data
msg = "command"
msg = msg.encode(encoding="utf-8") 
sent = sock.sendto(msg, tello_address)

msg = "speed 50"
msg = msg.encode(encoding="utf-8") 
sent = sock.sendto(msg, tello_address)

print("READY TO FLY")

while True:
	try:
		msg = str(msvcrt.getch())
		for key, value in msg_decoder.items():
			if key in msg:
				msg = value
				break

		if not msg:
			break  

		if 'end' in msg:
			print ('...')
			sock.close()  
			break

		# Send data
		msg = msg.encode(encoding="utf-8") 
		sent = sock.sendto(msg, tello_address)
		
	except KeyboardInterrupt:
		print ('\n . . .\n')
		sock.close()  
		break
		

#---------------------- IOTDeviceSocket.py----------------------
#This Class is only meant for Sending/Receiving Data using sockets at IOT Device Side

import socket
import sys

MAX_BUFFER_SIZE = 4096 #Maximum Buffer of 4096 Bytes

class ClientSocket:
	
	def __init__(self): #initializer when object is created
		print("Client socket started....")
		self.soc = None

	def send_to_Server(self, data): # to encode and send data to server
		self.soc.send(data.encode("hex"))

	def receive_from_Server(self): # to receive and decode data from server
		msg = self.soc.recv(MAX_BUFFER_SIZE)
		return msg.decode("hex")
	
	def start_client(self): # to start the client socket
		self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print('Enter IP Address:')
		IP_ADD = raw_input()
		if (IP_ADD is 'l'): #for running on localhost, enter 'l'
			IP_ADD = 'localhost'
		print('Enter Port Number:')
		PORT_NUM = int(raw_input())
		self.soc.connect((IP_ADD, PORT_NUM))
		print('Client connected....')

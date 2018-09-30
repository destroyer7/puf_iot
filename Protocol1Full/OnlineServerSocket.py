#---------------------- OnlineServerSocket.py----------------------
#This Class is only meant for Sending/Receiving Data using sockets at Server Side

import sys
import socket
import traceback

MAX_BUFFER_SIZE = 4096

class ServerSocket:

    def __init__(self): #initializer when object is created
        print("Server socket started....")
        self.soc = None
        self.conn = None
        self.ip = None
        self.port = None

    def send_to_Client(self, data): # to encode and send data to client
        msg = data.encode("hex")  # encoding 
        self.conn.send(msg)

    def receive_from_Client(self): # to receive and decode data from client
        msg = self.conn.recv(MAX_BUFFER_SIZE)
        return msg.decode("hex")

    def end_connection(self): # to close server socket connection
        print('End of the journey... Until next time...')
        self.conn.close()  # closing connection
        print('Connection ' + self.ip + ':' + self.port + " ended")

    def start_server(self): # to start server socket
        
        print('Enter IP Address:')
        IP_ADD = raw_input()
        if (IP_ADD is 'l'): #for running on localhost, enter 'l'
          IP_ADD = 'localhost'
        print('Enter Port Number:')
        PORT_NUM = int(raw_input())
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Socket created....')

        try:
            self.soc.bind((IP_ADD, PORT_NUM))
            print('Socket bind complete....') #binding
        except socket.error as msg:
            print('Bind failed. Error : ' + str(sys.exc_info()))
            sys.exit()

        # listening
        self.soc.listen(10)
        print('Socket now listening...')

        self.conn, addr = self.soc.accept()
        self.ip, self.port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + self.ip + ':' + self.port)
        print('Server connected....')
        self.soc.close()
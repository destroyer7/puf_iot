#---------------------- DriverIOTDevice.py----------------------

import sys # For system functions
from IOTDeviceSocket import ClientSocket # For Server-Client Communication using TCP Sockets
from IOTDeviceCrypto import IOTCrypto # For Cryptographic Functions

def client_driver_protoOne():

	print('------------------------------------------------------------------------------------------------------------------------')
	#Creating objects for the imported classes

	IDa = 'raspberrypi@1234' 
	clsoc_obj = ClientSocket()
	iot_obj = IOTCrypto(IDa)

	clsoc_obj.start_client()

	print('------------------------------------------------------------------------------------------------------------------------')
	#Preprocessing before sending Message 1
	print('Generating Random Nonce N1: ')
	N1 = iot_obj.generate_Random(8)
	print('N1: {}\n\n'.format(N1))

	MSG = IDa+N1

	print('\nSending message from Online Server')

	print('\nSending the Message IDa||N1: : '+MSG)
	clsoc_obj.send_to_Server(MSG)

	print('------------------------------------------------------------------------------------------------------------------------')
	#Postprocessing after receiving Message 2 and before sending Message 3
	print('\nReceiving message from Online Server')
	MSG = clsoc_obj.receive_from_Server()

	print('\nMessage received from server: '+MSG)
	Ci1 = MSG[0:16]
	MA = MSG[16:64]
	MACval = MSG[64:]

	Ri1 = iot_obj.PUF(Ci1)

	print('\nReceived Challenge Ci1 :'+Ci1+'\n')
	print('\nReceived MA :'+MA+'\n')
	print('\nReceived MACval :'+MACval+'\n')

	print('\nGenerating Ri1: '+Ri1)

	dMA = iot_obj.decrypt_Data(MA, Ri1)
	print('\nMA after decrypting with Ri1: '+dMA+'\n\n')

	Rs1 = dMA[24:]
	print('\nReceived Random Nonce Rs1: '+Rs1+'\n')

	MACmsg = MA+Ri1+Rs1

	print('\nVerifying MAC')
	if (not iot_obj.verify_MAC(IDa,MACmsg,MACval)):
		print("\nTerminating Program...")
		sys.exit()

	print('Generating Random Nonce Na: ')
	Na = iot_obj.generate_Random(8)
	print('\nNa: '+Na)


	print('Generating Ci2 by hashing Na and Rs1: ')
	Ci2 = iot_obj.generate_Hash(Na+Rs1)
	Ri2 = iot_obj.PUF(Ci2)

	print('\nCi2: '+Ci2)

	print('\nRi2: '+Ri2)

	ms = IDa+Rs1+Na+Ri2 #16+8+8+16

	print('\nMS before encrypting with Ri1: '+ms+'\n\n')
	MS = iot_obj.encrypt_Data(ms,Ri1)
	print('\nMS after encrypting with Ri1: '+MS+'\n\n')

	MACmsg = MS+Ri1+Na
	print('\nGenerating MAC of MACmsg')
	MACval = iot_obj.sign_MAC(IDa, MACmsg)
	print('\nMACval of MACmsg: '+MACval+'\n\n')
	
	MSG = MS + MACval

	print('\nMessage to be sent to Online Server: '+MSG+'\n\n')
	print('\nSending message to IOT Device')
	clsoc_obj.send_to_Server(MSG)

	print('\n\nMutual Authentication achieved!')

	print('------------------------------------------------------------------------------------------------------------------------')
	#Post Processing after achieving Mutual Authentication

	hashRs1 = iot_obj.generate_Hash(Rs1)
	hashNa = iot_obj.generate_Hash(Na)

	session_key = ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(hashRs1,hashNa))

	print('\nSession Key: '+session_key+'\n\n')

client_driver_protoOne()
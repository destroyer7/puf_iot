#---------------------- DriverOnlineServer.py----------------------

import sys
from OnlineServerSocket import ServerSocket # For Server-Client communication using TCP sockets
from OnlineServerCrypto import ServerCrypto # For Cryptographic Functions
from IOTDatabase import database_server # For the Database

def device_driver_protoOne():

	#Creating objects for the imported classes
	sersoc_obj = ServerSocket()
	ons_obj = ServerCrypto()
	db_con = database_server()

	db_con.startDBConnection()

	db_con.create_table()
	print('Database created!')

	print('Inserting ID, CRP in Database')

	# Assuming we have the IOT Device ID and CRP at startup
	ID = 'raspberrypi@1234'
	C = 'qwertyASDFGH@012'
	R = '48f8878e987de1b86d9f95614227b625'
	R = R.decode('hex')

	db_con.insert_entry(ID,C,R)
	print('\nID, CRP is inserted successfully')
	print('\nContents of database:')
	db_con.display_entries()

	print('------------------------------------------------------------------------------------------------------------------------')
	
	sersoc_obj.start_server()
	
	print('------------------------------------------------------------------------------------------------------------------------')
	#Postprocessing after receiving Message 1 and preprocessing before sending Message 2
	print('\nReceiving message from IOT Device')
	MSG = sersoc_obj.receive_from_Client()
	print('\n\nMessage received from client: '+MSG)
	IDa = MSG[0:16]
	N1 = MSG[16:24]
	print('\nReceived ID: '+IDa)
	print('\nReceived Nonce N1: '+N1)

	print('\nQuerying database to get CRP')
	rec = db_con.return_entry(IDa)
	print('\nID found in Database! Proceed!\n')
	Ci1 = rec[0]
	Ri1 = rec[1]
	print('\nCi1: '+Ci1)
	print('\nRi1: '+Ri1)

	print('\nGenerate Random Nonce Rs1')
	Rs1 = ons_obj.generate_Random(8)
	print('\nRs1 generated: '+Rs1)

	ma = ID+N1+Rs1 #16+8+8=32
	print('\nMA before encrypting with R1: '+ma+'\n\n')
	MA = ons_obj.encrypt_Data(ma,Ri1)
	print('\nMA after encrypting with R1: '+MA+'\n\n')

	MACmsg = MA+Ri1+Rs1 #32+16+8=56x2=112
	print('\nGenerating MAC of MACmsg')
	MACval= ons_obj.sign_MAC(IDa,MACmsg) #16
	print('\nMACval of MACmsg: '+MACval+'\n\n')	
	MSG = Ci1+MA+MACval #16+32+16

	print('\nMessage to be sent to IOT Device: '+MSG+'\n')
	print('Sending message to IOT Device')
	sersoc_obj.send_to_Client(MSG)
	print('------------------------------------------------------------------------------------------------------------------------')
	#Postprocessing after receiving Message 3

	print('\nReceiving message from IOT Device')
	MSG = sersoc_obj.receive_from_Client()

	if (MSG==""):
		print("Mutual Authentication rejected!")
		sys.exit()

	print('\n\nMessage received from IOT Device: '+MSG)

	MS = MSG[0:64]
	MACval = MSG[64:]

	print('\nReceived MS: '+MS)
	print('\nReceived MACval: '+MACval)

	print('\nMS before decrypting with Ri1: '+MS+'\n\n')
	dMS = ons_obj.decrypt_Data(MS, Ri1)
	print('\nMS after decrypting with Ri1: '+dMS+'\n\n')

	Na = dMS[24:32]
	print('\nRandom Nonce Na: '+Na)

	Ri2 = dMS[32:]
	print('\nResponse Ri2: '+Ri2+'\n')

	MACmsg = MS+Ri1+Na

	print('\nVerifying MAC')
	if (not ons_obj.verify_MAC(IDa,MACmsg,MACval)):
		print("\nTerminating Program...")
		sys.exit()

	print('\nCreating Ci2')
	Ci2 = ons_obj.generate_Hash(Na+Rs1)
	print('\nCi2: '+Ci2+'\n')
	print('\nMutual Authentication achieved!\n')

	print('------------------------------------------------------------------------------------------------------------------------')

	#Post Processing after achieving Mutual Authentication

	hashRs1 = ons_obj.generate_Hash(Rs1)
	hashNa = ons_obj.generate_Hash(Na)
	session_key = ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(hashRs1,hashNa))

	print('\n\nSession Key: '+session_key+'\n\n')

	print('\nUpdate ID, CRP in Database!')
	db_con.update_entry(IDa,str(Ci2),str(Ri2))
	print("\nUpdated CRP for IDa")
	print('\nContents of database:')
	db_con.display_entries()

	db_con.drop_table()
	#print('Table dropped successfully')
	
	sersoc_obj.end_connection()

device_driver_protoOne()
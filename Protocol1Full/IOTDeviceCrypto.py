#------------------- IOTDeviceCrypto.py ---------------------
#This Class is only meant for implementing Cryptographic functions at IOT Device Side
from Crypto.Hash import CMAC, MD5
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Padding
from BitVector import *
import random

class IOTCrypto:

	def __init__(self, ID): #initializer when object is created
		print("The IOT Device has started")
		self.ID = ID

	def PUF(self, challenge): #Software version of Physical Unclonable Functions using ID and hash
		response = ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(self.ID,challenge)) # ID xor challenge
		hresponse = self.generate_Hash(response) # response = Hash(ID xor challenge)
		return hresponse

	def generate_Random(self, length): #generating random number of bytes
		return Random.get_random_bytes(length)

	def generate_Hash(self, data): #creating 128 bit MD5 Hash
		hash_object = MD5.new()
		hash_object.update(data)
		return hash_object.hexdigest().decode('hex')

	def encrypt_Data(self, data, key): #encrypting the data by AES (128 bit)
		data = Padding.pad(data, 16, 'pkcs7')
		cipher = AES.new(key, AES.MODE_ECB)
		cipher_text = cipher.encrypt(data)
		return cipher_text

	def decrypt_Data(self, data, key): #decrypting the data by AES (128 bit)
		cipher = AES.new(key, AES.MODE_ECB)
		plain_text = cipher.decrypt(data)
		plain_text = Padding.unpad(plain_text, 16, 'pkcs7')
		return plain_text

	def sign_MAC(self, secret, message): #creating MAC via CMAC
		mac_object = CMAC.new(secret, ciphermod=AES)
		mac_object.update(msg= message)
		return mac_object.hexdigest()

	def verify_MAC(self, secret, message, tag): #verifying MAC via CMAC
		mac_object = CMAC.new(secret, ciphermod=AES)
		mac_object.update(msg=message)
		try:
			mac_object.hexverify(tag)
			print("The message is authentic. Proceed!")
			return 1
		except ValueError:
			print("The message or the key is wrong! Authentication Unsuccessful!")
			return 0

	def corrupt_Bit(self, message): #Corrupting 1 random bit of message
		bv_msg = BitVector(textstring= message)
		list_bv_msg = list(bv_msg)
		index = random.randint(0,len(message))
		list_bv_msg[index] = (int(list_bv_msg[index])+1)%2
		corr_msg = ''.join(str(list_bv_msg[i]) for i in range(len(list_bv_msg)))
		corr_bv_msg = BitVector(bitstring=corr_msg)
		return corr_bv_msg.get_bitvector_in_ascii()
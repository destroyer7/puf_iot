import time

from random import shuffle
from PUF import SerialPUF, Tools
import threading

serialconnection1='/dev/ttyACM0'
serialconnection2='/dev/ttyACM1'
serialconnection3='/dev/ttyACM2'
serialconnection4='/dev/ttyACM3'
bitrate=115200

fpc = open("C.TXT","r")
lines_list_c = fpc.readlines()
challenge = [[int(val) for val in line.split()] for line in lines_list_c[0:]]
print(challenge)

fph = open("H.TXT","r")
lines_list_h = fph.readlines()
helper = [[int(val) for val in line.split()] for line in lines_list_h[0:]]
print(helper)

# Initialize serial connection to connect to Arduino
serialPUF = SerialPUF.SerialPUF()
if not serialPUF.connect(serialconnection1,bitrate):
    if not serialPUF.connect(serialconnection2,bitrate):
        if not serialPUF.connect(serialconnection3,bitrate):
            if not serialPUF.connect(serialconnection4,bitrate):
                print("Error connecting to Arduino")
                exit(1)
time.sleep(2)

serialPUF.check_if_it_is_working()

serialPUF.write_challenges_to_sd(challenge[:37 * 63])
serialPUF.write_helper_to_sd(helper[:37 * 63])



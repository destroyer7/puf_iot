import time

from random import shuffle
from PUF import SerialPUF, Tools
import threading

def read_integers(filename):
    with open(filename) as f:
        return [int(x) for x in f]

serialconnection1='/dev/ttyACM0'
serialconnection2='/dev/ttyACM1'
serialconnection3='/dev/ttyACM2'
serialconnection4='/dev/ttyACM3'
bitrate=115200

challenge = read_integers("C.TXT")
print(challenge)

helper = read_integers("H.TXT")
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

# serialPUF.check_if_it_is_working()

serialPUF.write_challenges_to_sd(challenge[:37 * 63])
serialPUF.write_helper_to_sd(helper[:37 * 63])
key32 = serialPUF.get_keys()
print(key32)


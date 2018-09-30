import binascii

def read_integers(filename):
    with open(filename) as f:
        return [int(x) for x in f]

key = read_integers("K.TXT")
for item in key:
    print(hex(item))

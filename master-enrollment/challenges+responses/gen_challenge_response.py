from random import shuffle
import numpy as np
import os

def save_challenge(new_stable_bits,x):
    challenge = new_stable_bits[:,0]
    np.savetxt('c%d.txt' %x, challenge, fmt = '%d', newline='\n')
    return None

def save_response(new_stable_bits,x):

    response = new_stable_bits[:,1]
    
    #pad zeros to the end to make x 2336 in length.
    N = 5
    response = np.pad(response,(0,N),'constant')

    f = open("r%d.txt" %x,"w",encoding="utf8")
    #np.savetxt('r%d.txt' %x, response, fmt = '%d', newline='\n') #These are responses
    
    #converting to uint7_t format
    i = 0;
    while (i < 2336):
        a0 = response[i]
        a1 = response[i+1]
        a2 = response[i+2]
        a3 = response[i+3]
        a4 = response[i+4]
        a5 = response[i+5]
        a6 = response[i+6]
        a7 = response[i+7]

        binary = a7 + 2 * a6 + 4 * a5 + 8 * a4 + 16 * a3 + 32 * a2 + 64 * a1
        f.write("%d\n"%int(binary))
        #don't print new line character on the last iteration.
        i = i + 8
    f.close()
    
fp = open("bitsinfo.txt","r")
lines_list = fp.readlines()
my_data = [[int(val) for val in line.split()] for line in lines_list[0:]]

stable_bits = np.zeros((4662,2))
row = 0
column = 0

for item in my_data:
    stable_bits[row][0] = item[0]
    
    if row < 2331:
        stable_bits[row][1] = 0
    else:
        stable_bits[row][1] = 1
    row = row + 1

stable_bits = np.intc(stable_bits)

# currdir = os.getcwd()
# directory = currdir + "/challenges+responses"
# if not os.path.exists(directory):
#     os.makedirs(directory)
# os.chdir(directory)

no_of_responses = 10

for x in range(no_of_responses):
    new_stable_bits = stable_bits
    np.random.shuffle(new_stable_bits) #Shuffle along first dimension
    save_challenge(new_stable_bits[0:2331],x)
    save_response(new_stable_bits[0:2331],x)

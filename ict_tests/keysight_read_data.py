#!/usr/bin/env python

import visa
import time
import datetime
import sys
import os

#### SCRIPT SETTINGS ####

# oscilloscope channel
channel_a = 1
channel_b = 2

#########################

# connection
if 'rm' in globals():
    pass
else:
    global rm
    rm = visa.ResourceManager('@py')

# oscilloscope IP
ip = "10.128.151.74"
filename = "osc_keysight_"+str(datetime.datetime.now())

# open connection
osc_socket = rm.open_resource('TCPIP::'+ip+'::inst0::INSTR')
print 'Connected'

# set timeout
osc_socket.timeout = 25000

# choose osc channel
osc_socket.write(':WAVeform:SOURce CHANnel'+str(channel_a))

time.sleep(1)

# save TDR response
with open(filename+'chan'+str(channel_a), 'a') as f:
    data = osc_socket.query(':WAVeform:DATA?')
    f.write("\n")
    f.write(data)

#time.sleep(4)

# choose osc channel
#osc_socket.write(':WAVeform:SOURce CHANnel'+str(channel_b))

# save TDR response
#with open(filename+'chan'+str(channel_b), 'a') as f:
#    data = osc_socket.query(':WAVeform:DATA?')
#    f.write("\n")
#    f.write(data)

osc_socket.close()

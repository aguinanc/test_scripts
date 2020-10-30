#!/usr/bin/env python3

import socket
import argparse
import sys

# parse input args
parser = argparse.ArgumentParser()
parser.add_argument('-i', action="store", dest="ip", type=str, help="Device IP address", required=True)
parser.add_argument('-p', action="store", dest="port", type=int, default=5025, help="device port")
parser.add_argument('-t', action="store", dest="terminator", default='\n', help="termination character")
# le argumentos e escreve nas variaveis
args = parser.parse_args()

ip = args.ip
port = args.port
term = args.terminator

# create TCPIP socket
try:
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.connect((ip, port))
except:
  print("Failed to connect to device") 
  sys.exit(-1)

# read messages typed by user and receive
# responses from device
while True:
    # get cmd from user
    cmd = input('cmd>')
    # check abort cmd
    if cmd == 'exit' or cmd == 'close':
        sock.close()
        break
    # send cmd
    sent = sock.send(cmd)
    if sent == 0:
        raise RuntimeError('connection is broken')
    # read response
    resp = []
    byte = '@'
    while byte != term:
        byte = sock.recv(1)
        if byte == b'':
            raise RuntimeError('connection is broken')
        resp.append(byte)
    print('resp>'+str(resp))

# end script
sys.exit(0)

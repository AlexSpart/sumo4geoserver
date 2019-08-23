#!/usr/bin/env python3
#DGRAM

# -*- coding: utf-8 -*-
import socket
import os

server_address = "/tmp/INVM_SAP"

if os.path.exists(server_address):
    os.remove(server_address)

print("Opening socket...")
server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
# Bind the socket to the file
server.bind(server_address)
print('Starting up on {}'.format(server_address))

print("Listening...")
while True:
    # Wait for a connection
    datagram = server.recv(1024)
    if not datagram:
        break
    else:
        print("-" * 20)
        print(datagram.decode('utf-8'))
        if "DONE" == datagram.decode('utf-8'):
            break
print("-" * 20)
print("Shutting down...")
server.close()
#CLEAN THE file after the connection
#os.remove("/tmp/python_unix_sockets_example")
print("Done")

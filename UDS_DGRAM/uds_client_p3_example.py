#!/usr/bin/env python

# -*- coding: utf-8 -*-
import socket
import os

print("Connecting...")
server_address = "/tmp/INVM_SAP"
print('connecting to {}'.format(server_address))

if os.path.exists(server_address):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    client.connect(server_address)
    print("Ready.")
    print("Write a message inside''")
    print("Ctrl-C to quit.")
    print("Sending 'DONE' shuts down the server and quits.")
    while True:
        try:
            x = input("> ")
            if "" != x:
                print("SEND:", x)
                client.send(x.encode('utf-8'))
                if "DONE" == x:
                    print("Shutting down.")
                    break
        except KeyboardInterrupt as k:
            print("Shutting down.")
            client.close()
            break
else:
    print("Couldn't Connect!")
print("Done")

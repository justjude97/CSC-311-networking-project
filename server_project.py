import socket
import os
import struct

"""
    AF_INET - ipv4
    SOCK_STREAM - tcp protocol
"""
#create the socket in preperation for binding
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#port can be anything
port = 12345
#binds to the port
sock.bind(('', port))
print("socket binded to %s" %(port))

#server will keep running indefinitely, until it is closed
while True:
    #the server will keep 5 connections waiting, the sixth one will be rejected
    sock.listen(1)

    while True:
        c, address = sock.accept()
        print("got connection from", address)

        #command reads what the commands were so that the loop can exit
        command = processAction()

        if(command = "close"):
            c.close()
            break

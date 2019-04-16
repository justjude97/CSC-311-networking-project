import socket
import os
import struct

class ftpSock:
    pass

#this method was 'inspired' by the stacks overflow answer at:
#   https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

#this solution seems necessary as the recv will straight-up ignore bytes
#   if it doesn't get them on time
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    print("datSize: ", len(data))
    while len(data) < n:
        packet = sock.recv(n - len(data))
        print(packet)
        if packet:
            data += packet

    return data

def getFile(sock, fileName):

    #gets the fileSize
    data = recvall(sock, 4)
    print("data", data)

    if not data:
        return None

    fileSize = struct.unpack("!I", data)[0]

    fileContents = recvall(sock, fileSize)
    fileContents = fileContents.decode("utf_8")
    
    print(fileContents)
    #TODO implement a way to send the file to any destination provided by a third argument
    file = open(fileName, "w")
    file.write(fileContents)

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

    c, address = sock.accept()
    print("got connection from", address)

    #login
    print("logic credentials:")
    c.sendall("ID?: ".encode("utf-8"))
    account = c.recv(1024)
    print(account.decode("utf-8"))

    c.sendall("password?: ".encode("utf-8"))
    password = c.recv(1024)
    print(password.decode("utf-8"))

    while True:


        datSize = recvall(c, 4)
        print(datSize)
        datSize = struct.unpack("!I", datSize)[0]
        print(datSize)
        dat = recvall(c, datSize)

        if not c:
            print("bad")
            continue
        #data = c.recv(8)
        #data = data.decode()
        dataLine = dat.decode("utf-8")

        print(dataLine)


        command = dataLine.split(" ")[0]

        if(command == "ls" or command == "dir"):
            dirContents = os.listdir(os.getcwd())
            dirString = " ".join(dirContents)

            c.sendall(dirString.encode("utf-8"))
        elif(command == "cd"):
            arg = dataLine.split(" ")[1]
            os.chdir(arg)
            print(arg)

            c.sendall(os.getcwd().encode("utf-8"))
        elif(command == "get"):
            #attempts to get the filepath
            filePath = dataLine.split(" ")[1]
            #this is just to get rid of the newline sent across
            filePath = filePath.rstrip()

            file = open(filePath, 'r')
            fileName = os.path.basename(filePath)
            fileSize = os.path.getsize(filePath)
            fileContents = file.read()

            message = struct.pack("!I", len(fileName)) + fileName.encode("utf_8") + struct.pack("!I", fileSize) + fileContents.encode("utf_8")
            c.sendall(message)
        elif(command == "put"):
            #attempts to get the filepath
            filePath = dataLine.split(" ")[1]

            #this gets the basename of the file, or it should since the basename should be at the end of the filepath
            fileName = (filePath.split("\\"))[-1]
            fileName = fileName.rstrip()

            getFile(c, fileName)



        inp = input()
        c.sendall(inp.encode("utf-8"))

        #print(msg)
        #command reads what the commands were so that the loop can exit
        #command = processAction(sock)

        #if(command == "close"):
        #    c.close()
        #    break

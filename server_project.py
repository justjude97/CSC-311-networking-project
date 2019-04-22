import socket
import os
import struct

#this method was based off the geeks for geeks article on wildcard matching
#https://www.geeksforgeeks.org/wildcard-pattern-matching/
def strMatch(input=str(), pattern=str()):

    #if the pattern is the empty string, it can only match the empty string
    if len(pattern) == 0:
        if len(input) == 0:
            return True
        else:
            return False

    matchTable = []

    #x is the input
    #y is the pattern
    for x in range(0, len(input)+1):

        matchTable.append([])
        for y in range (0, len(pattern)+1):
            matchTable[x].append(False)

    #"empty pattern can match with empty string"
    #in other works, the [0][0] indice indicates that no character have been consumed yet
    matchTable[0][0] = True

    for x in range(1, len(pattern)+1):
        if pattern[x-1] == '*':
            matchTable[0][x] = matchTable[0][x-1]

    for x in range(1, len(input)+1):
        for y in range(1, len(pattern)+1):

            #case 1 - astrisk:
            if pattern[y-1] == '*':
                matchTable[x][y] = matchTable[x][y-1] or matchTable[x-1][y]

            #case 2 next character in pattern is a ? or patterns match
            elif pattern[y-1] == '?' or input[x-1] == pattern[y-1]:
                matchTable[x][y] = matchTable[x-1][y-1]
            #case 3 current characters in input and pattern down match
            else:
                matchTable[x][y] = False

    #return the last column of the last row, which contains our answer
    return matchTable[-1][-1]

#this method was taken from a stacks overflow answer at:
#   https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data

#this solution seems necessary as the recv will straight-up ignore bytes
#   if it doesn't get them on time
def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    print("datSize: ", len(data))
    while len(data) < n:
        print("hi")

        packet = sock.recv(n - len(data))

        if not packet:
            return None

        print(packet)
        if packet:
            data += packet

    return data

def getMessage(sock):
    #get the 4 byte header indicating the length
    data = recvall(sock, 4)
    if not data:
        return None
    else:
        fileSize = struct.unpack("!I", data)[0]

        if fileSize != -1:
            return recvall(sock, fileSize)
        else:
            return None


#gets the data from getMessage(), but writes it to a file
def getFile(sock, fileName):

    fileContents = getMessage(sock)

    if fileContents != None:
        #TODO implement a way to send the file to any destination provided by a third argument
        file = open(fileName, "wb")
        file.write(fileContents)

def sendMessage(sock, message):

    packet = struct.pack("!I", len(message)) + message.encode("utf_8")
    sock.sendall(packet)

#same as sendMessage, but already assumes that the message is a bytestring
def sendFile(sock, message):

    packet = struct.pack("!I", len(message)) + message
    sock.sendall(packet)



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
        dat = recvall(c, datSize)
        print(dat)

        if not c:
            print("bad")
            continue

        dataLine = dat.decode("utf-8")

        print(dataLine)


        command = dataLine.split(" ")[0]

        if(command == "ls" or command == "dir"):
            dirContents = os.listdir(os.getcwd())
            dirString = " ".join(dirContents)

            sendMessage(c, dirString)
            print("done sending")

        elif(command == "cd"):
            arg = dataLine.split(" ")[1]
            os.chdir(arg)
            print(arg)

            sendMessage(c, os.getcwd())
            print("done changing")

        elif(command == "get"):
            #attempts to get the filepath
            filePath = dataLine.split(" ")[1]
            #this is just to get rid of the newline sent across
            filePath = filePath.rstrip()

            file = open(filePath, 'rb')
            fileSize = os.path.getsize(filePath)

            fileContents = file.read()

            message = struct.pack("!I", fileSize) + fileContents
            sendFile(c, message)

        elif(command == "put"):
            #attempts to get the filepath
            filePath = dataLine.split(" ")[1]

            #this gets the basename of the file, or it should since the basename should be at the end of the filepath
            fileName = (filePath.split("\\"))[-1]
            fileName = fileName.rstrip()

            getFile(c, fileName)

        elif(command == "mget"):

            fileNames = os.listdir(os.getcwd())
            pattern = dataLine.split(" ")[2]

            for name in fileNames:
                if strMatch(name, pattern):
                    filePath = os.getcwd() + '\\' + name
                    file = open(filePath, 'rb')
                    fileContents = file.read()
                    file.close()

                    message = struct.pack("!I", len(name)) + name.encode("utf_8") + fileContents
                    sendFile(c, message)

            exitCode = struct.pack("!I", -1)
            c.sendall(exitCode)

        elif( command == "mput" ):
            fileSize = recvall(c, 4)
            fileSize = struct.unpack("!I", fileSize)[0]

            while fileSize != -1:
                fileNameSize = recvall(c, 4)
                if fileNameSize:
                    fileNameSize = struct.unpack("!I", fileNameSize)
                    fileName = recvall(c, fileNameSize)

                    fileSize = fileSize - (4 + fileName)
                    fileContents = recvall(c, fileSize)

                    file = open(fileName.decode("utf_8"), "wb")
                    file.write(fileContents)

                    fileContents = recvall(c, 4)
                    fileContents = struct.unpack("!I", fileContents)
                else
                    break

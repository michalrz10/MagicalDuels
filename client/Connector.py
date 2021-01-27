import socket
import threading
import enums
import time
import string
import random

class Server_Connector:
    def __init__(self):
        self.sock=None
        f=open('IpAddress')
        self.serverIp=f.read()
        print(self.serverIp)
        f.close()

    def connect(self):
        temp=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp.connect((self.serverIp,5000))
        data=temp.recv(1)
        if data==enums.ConnectionMessages.PORT.value:
            port=int.from_bytes(temp.recv(1),'big')+5001
            temp.close()
            print(port)
            self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print((self.serverIp,port))
            self.sock.connect((self.serverIp,port))
            print('connected')
        elif data==enums.ConnectionMessages.NO_FREE_PORT.value:
            print('No aveliable ports, try again later')
        else:
            raise Exception('Unknown return')

    def sendNickname(self,nickname):
        self.sock.send(enums.ConnectionMessages.NICKNAME.value)
        if len(nickname)>15: raise Exception("To long nick")
        self.sock.send(nickname.ljust(15).encode())

    def createLobby(self):
        self.sock.send(enums.ConnectionMessages.CREATE_GAME.value)

    def get_lobbies(self):
        self.sock.send(enums.ConnectionMessages.GET_LOBBIES.value)
        return int.from_bytes(self.sock.recv(1), 'big')

    def joinLobby(self,lobby):
        self.sock.send(enums.ConnectionMessages.GET_LOBBIES.value)
        number= int.from_bytes(self.sock.recv(1), 'big')
        if lobby>=number or lobby<0: raise Exception('No such lobby')
        self.sock.send(enums.ConnectionMessages.JOIN_GAME.value+lobby.to_bytes(1,'big'))

    def deconnect(self):
        self.sock.send(enums.ConnectionMessages.CLOSE.value)
        self.sock.close()


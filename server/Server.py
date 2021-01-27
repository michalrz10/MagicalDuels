import socket
import threading
import enums
from server import Logs
import time
import selectors
import types
from game import GameServer



class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.active = []
        self.players={}
        self.lobbies=[]
        self.games=[]
        self.running=True
        self.log = Logs.Log()
        self.connector=Connector(self)
        self.connector.start()
        self.sel=selectors.DefaultSelector()
        self.GuestNumber=0

    def addKlient(self,klient):
        self.active.append(klient)
        self.sel.register(klient,selectors.EVENT_READ,data=types.SimpleNamespace(inb=b'', outb=b''))
        self.GuestNumber+=1

    def run(self):
        while self.running:
            if (self.active != [] or self.players!={}) and self.GuestNumber>0:
                events = self.sel.select(timeout=0.1)
                for key, mask in events:
                    if key.data is None:
                        raise Exception('No data')
                    else:
                        sock = key.fileobj
                        data = sock.recv(1)
                        if data == enums.ConnectionMessages.CLOSE.value:
                            self.connector.ports[sock.getsockname()[1]-5001] = True
                            if sock in self.active:
                                self.active.remove(sock)
                            elif sock in self.players.keys():
                                self.players.pop(sock)
                            self.sel.unregister(sock)
                            self.GuestNumber -= 1
                            self.log.log(str(sock.getsockname()[0]) + ' close connection')
                            sock.close()
                        elif data == enums.ConnectionMessages.NICKNAME.value:
                            time.sleep(1)
                            nickname = sock.recv(15).decode()
                            while nickname[-1]==' ': nickname=nickname[:-1]
                            self.players[sock]=nickname
                            self.active.remove(sock)
                            self.log.log(str(sock.getsockname()[0]) + ' appty nickname: '+nickname)
                        elif data==enums.ConnectionMessages.CREATE_GAME.value:
                            self.lobbies.append([sock])
                            self.log.log(self.players[sock]+' created new lobby')
                        elif data == enums.ConnectionMessages.JOIN_GAME.value:
                            number=int.from_bytes(sock.recv(1),'big')
                            if number>len(self.lobbies): raise Exception('No such lobby')
                            self.lobbies[number].append(sock)
                            self.games.append(GameServer.GameServer(self, self.lobbies[number][0],self.lobbies[number][1]))
                            self.sel.unregister(self.lobbies[number][0])
                            self.sel.unregister(self.lobbies[number][1])
                            self.GuestNumber -= 2
                            self.lobbies.remove(self.lobbies[number])
                            self.games[-1].start()
                            self.log.log(self.players[sock] + ' joined lobby '+str(number))
                        elif data == enums.ConnectionMessages.GET_LOBBIES.value:
                            sock.send(len(self.lobbies).to_bytes(1,'big'))
                            self.log.log(self.players[sock] + ' gets lobbies ')
                        else:
                            raise Exception(data)

            else:
                time.sleep(0.05)

            for i in self.games:
                if i.finished:
                    print('Game ended')
                    self.GuestNumber += 2
                    self.sel.register(i.player1[0], selectors.EVENT_READ,
                                      data=types.SimpleNamespace(inb=b'', outb=b''))
                    self.sel.register(i.player2[0], selectors.EVENT_READ,
                                      data=types.SimpleNamespace(inb=b'', outb=b''))
                    self.games.remove(i)





class Connector(threading.Thread):
        def __init__(self,server):
            threading.Thread.__init__(self)
            self.port=5000
            self.running=True
            self.server=server
            self.ports=[True for _ in range(100)]

        def getFreeSocket(self):
            for i in range(len(self.ports)):
                if self.ports[i]:
                    self.ports[i] = False
                    return i
            return -1

        def run(self):
            while self.running:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('', self.port))
                sock.listen(1)
                connection, client_address = sock.accept()
                self.server.log.log('new connection: '+str(client_address))
                temp=sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tempPort=self.getFreeSocket()
                if tempPort>=0:
                    temp.bind(('', tempPort+5001))
                    connection.send(enums.ConnectionMessages.PORT.value+tempPort.to_bytes(1,'big'))
                    self.server.log.log('send port '+str(tempPort)+' to '+str(client_address))
                    temp.listen(1)
                    con, client_address = temp.accept()
                    con.setblocking(False)
                    self.server.addKlient(con)
                else:
                    connection.send(enums.ConnectionMessages.NO_FREE_PORT.value)
                    self.server.log.log('no free port for '+str(client_address))
                connection.close()
                sock.close()

Server().start()
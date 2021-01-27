import threading
import time
import socket
import enums
import selectors
import types
from game import Game
from game import spells
import math

class GameServer(threading.Thread):
    def __init__(self,server,playerSocket,player2Socket):
        threading.Thread.__init__(self)
        self.running = True
        self.server=server
        self.player1=[playerSocket]
        self.player2=[player2Socket]
        self.p1Messages=[]
        self.p2Messages=[]
        self.GAME_ITERATION_TIME=0.05
        self.MOVE_VALUE=10
        self.lockp1 = threading.Lock()
        self.lockp2 = threading.Lock()
        self.spells=[]
        self.finished=False


    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        sock.listen(1)
        self.player1[0].send(enums.ConnectionMessages.PORT.value + sock.getsockname()[1].to_bytes(2, 'big'))
        connection, client_address = sock.accept()
        self.player1.append(connection)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        sock.listen(1)
        self.player2[0].send(enums.ConnectionMessages.PORT.value + sock.getsockname()[1].to_bytes(2, 'big'))
        connection, client_address = sock.accept()
        self.player2.append(connection)
        p1Receiver=Receiver(self.p1Messages,self.player1[1],self.lockp1)
        p2Receiver=Receiver(self.p2Messages,self.player2[1],self.lockp2)
        p1Receiver.start()
        p2Receiver.start()
        start=time.time()
        p1=Game.Mage(None,320,360)
        p2=Game.Mage(None,980,360)
        while self.running:
            self.lockp1.acquire()
            try:
                for i in range(len(self.p1Messages)):
                    if self.p1Messages[i] == enums.GameMessages.MOVEN.value:
                        p1.moveTo(-self.MOVE_VALUE, 0)
                    elif self.p1Messages[i] == enums.GameMessages.MOVES.value:
                        p1.moveTo(self.MOVE_VALUE, 0)
                    elif self.p1Messages[i] == enums.GameMessages.MOVEE.value:
                        p1.moveTo(0, self.MOVE_VALUE)
                    elif self.p1Messages[i] == enums.GameMessages.MOVEW.value:
                        p1.moveTo(0, -self.MOVE_VALUE)
                    elif self.p1Messages[i] == enums.GameMessages.MOVENE.value:
                        p1.moveTo(-self.MOVE_VALUE, self.MOVE_VALUE)
                    elif self.p1Messages[i] == enums.GameMessages.MOVENW.value:
                        p1.moveTo(-self.MOVE_VALUE, -self.MOVE_VALUE)
                    elif self.p1Messages[i] == enums.GameMessages.MOVESE.value:
                        p1.moveTo(self.MOVE_VALUE, self.MOVE_VALUE)
                    elif self.p1Messages[i] == enums.GameMessages.MOVESW.value:
                        p1.moveTo(self.MOVE_VALUE, -self.MOVE_VALUE)
                    elif self.p1Messages[i] == enums.GameMessages.SPELL1.value:
                        self.spells.append(spells.Ball(None,int(p1.x+(p2.x-p1.x)/10),int(p1.y+(p2.y-p1.y)/10),int((p2.x-p1.x)/20),int((p2.y-p1.y)/20)))
                    elif self.p1Messages[i] == enums.GameMessages.SPELL2.value:
                        self.spells.append(spells.Shield(None,int(p1.x+(p2.x-p1.x)/10),int(p1.y+(p2.y-p1.y)/10),0,0))
                    elif self.p1Messages[i] == enums.GameMessages.SPELL3.value:
                        pass
                self.p1Messages.clear()
            finally:
                self.lockp1.release()

            self.lockp2.acquire()
            try:
                for i in range(len(self.p2Messages)):
                    if self.p2Messages[i] == enums.GameMessages.MOVEN.value:
                        p2.moveTo(-self.MOVE_VALUE, 0)
                    elif self.p2Messages[i] == enums.GameMessages.MOVES.value:
                        p2.moveTo(self.MOVE_VALUE, 0)
                    elif self.p2Messages[i] == enums.GameMessages.MOVEE.value:
                        p2.moveTo(0, self.MOVE_VALUE)
                    elif self.p2Messages[i] == enums.GameMessages.MOVEW.value:
                        p2.moveTo(0, -self.MOVE_VALUE)
                    elif self.p2Messages[i] == enums.GameMessages.MOVENE.value:
                        p2.moveTo(-self.MOVE_VALUE, self.MOVE_VALUE)
                    elif self.p2Messages[i] == enums.GameMessages.MOVENW.value:
                        p2.moveTo(-self.MOVE_VALUE, -self.MOVE_VALUE)
                    elif self.p2Messages[i] == enums.GameMessages.MOVESE.value:
                        p2.moveTo(self.MOVE_VALUE, self.MOVE_VALUE)
                    elif self.p2Messages[i] == enums.GameMessages.MOVESW.value:
                        p2.moveTo(self.MOVE_VALUE, -self.MOVE_VALUE)
                    elif self.p2Messages[i] == enums.GameMessages.SPELL1.value:
                        self.spells.append(spells.Ball(None,int(p2.x+(p1.x-p2.x)/10),int(p2.y+(p1.y-p2.y)/10),int((p1.x-p2.x)/20),int((p1.y-p2.y)/20)))
                    elif self.p2Messages[i] == enums.GameMessages.SPELL2.value:
                        self.spells.append(spells.Shield(None,int(p2.x+(p1.x-p2.x)/10),int(p2.y+(p1.y-p2.y)/10),0,0))
                    elif self.p2Messages[i] == enums.GameMessages.SPELL3.value:
                        pass
                self.p2Messages.clear()
            finally:
                self.lockp2.release()

            for i in self.spells: i.iteration()

            for i in self.spells:
                for j in self.spells:
                    if i!=j:
                        if math.sqrt((i.x-j.x)**2+(i.y-j.y)**2)<=30:
                            i.collision(j)
                if math.sqrt((i.x - p1.x) ** 2 + (i.y - p1.y) ** 2) <= 30:
                    i.collision(p1)
                if math.sqrt((i.x - p2.x) ** 2 + (i.y - p2.y) ** 2) <= 30:
                    i.collision(p2)

            for i in self.spells:
                if i.crash or i.x<0 or i.y<0 or i.x>1280 or i.y>720:
                    self.spells.remove(i)

            if p1.crash or p2.crash:
                self.running=False
                self.finished=True
                self.player1[0].send(enums.GameMessages.END.value)
                self.player2[0].send(enums.GameMessages.END.value)
            else:
                self.player1[0].send(
                    enums.GameMessages.PLAYER1.value + p1.x.to_bytes(2, 'big') + p1.y.to_bytes(2, 'big'))
                self.player2[0].send(
                    enums.GameMessages.PLAYER1.value + p1.x.to_bytes(2, 'big') + p1.y.to_bytes(2, 'big'))
                for i in self.spells:
                    if i.name == 'shield':
                        self.player1[0].send(
                            enums.GameMessages.SPELL2.value + i.x.to_bytes(2, 'big') + i.y.to_bytes(2, 'big'))
                        self.player2[0].send(
                            enums.GameMessages.SPELL2.value + i.x.to_bytes(2, 'big') + i.y.to_bytes(2, 'big'))
                    if i.name == 'ball':
                        self.player1[0].send(
                            enums.GameMessages.SPELL1.value + i.x.to_bytes(2, 'big') + i.y.to_bytes(2, 'big'))
                        self.player2[0].send(
                            enums.GameMessages.SPELL1.value + i.x.to_bytes(2, 'big') + i.y.to_bytes(2, 'big'))

                self.player1[0].send(
                    enums.GameMessages.PLAYER2.value + p2.x.to_bytes(2, 'big') + p2.y.to_bytes(2, 'big'))
                self.player2[0].send(
                    enums.GameMessages.PLAYER2.value + p2.x.to_bytes(2, 'big') + p2.y.to_bytes(2, 'big'))


            waitTime=start+self.GAME_ITERATION_TIME-time.time()
            if waitTime>0: time.sleep(waitTime)
            start=time.time()
        p1Receiver.running=False
        p2Receiver.running=False

class Receiver(threading.Thread):
    def __init__(self,messages,playerSocket,lock):
        threading.Thread.__init__(self)
        self.messages=messages
        self.playerSocket=playerSocket
        playerSocket.setblocking(False)
        self.selector = selectors.DefaultSelector()
        self.selector.register(playerSocket, selectors.EVENT_READ, data=types.SimpleNamespace(inb=b'', outb=b''))
        self.running=True
        self.lock=lock

    def run(self):
        while self.running:
            events = self.selector.select(timeout=0.1)
            for key, mask in events:
                if key.data is None:
                    raise Exception('No data')
                else:
                    sock = key.fileobj
                    data = sock.recv(1)
                    self.lock.acquire()
                    try:
                        self.messages.append(data)
                    finally:
                        self.lock.release()

        self.selector.unregister(self.playerSocket)
        self.playerSocket.close()
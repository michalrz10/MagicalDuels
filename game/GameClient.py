from game import Game as gameClass
import pygame
import threading
import selectors
import socket
import types
import enums
from PIL import Image
import os
from game import spells

class Game:
    def __init__(self,playerSocket):
        self.background=pygame.image.frombuffer(Image.open('images\\background.png').tobytes(),(1280, 720),'RGBA')
        #self.background=pygame.image.load('..\\images\\background.png')
        mage=pygame.image.frombuffer(Image.open('images\\mage.png').tobytes(),(60,90),'RGBA')
        #mage=pygame.image.load('..\\images\\mage.png')
        self.player1=gameClass.Mage(mage,0,0)
        self.player2=gameClass.Mage(mage,0,0)
        self.receiver=Receiver(playerSocket,self)
        self.receiver.start()
        self.spellss=[]
        self.finished=False

    def draw(self,window):
        window.blit(self.background,(0,0))
        self.player1.draw(window)
        self.player2.draw(window)
        for i in self.spellss:
            i.draw(window)

    def end(self):
        self.receiver.running=False
        self.receiver.playerSocket.setblocking(True)
        self.finished=True
        print('End')

class Receiver(threading.Thread):
    def __init__(self,playerSocket,game):
        threading.Thread.__init__(self)
        playerSocket.setblocking(False)
        self.selector = selectors.DefaultSelector()
        self.playerSocket=playerSocket
        self.selector.register(playerSocket, selectors.EVENT_READ, data=types.SimpleNamespace(inb=b'', outb=b''))
        self.running=True
        self.game=game
        self.ball = pygame.image.frombuffer(Image.open('images\\ball.png').tobytes(), (30, 30), 'RGBA')
        self.shield = pygame.image.frombuffer(Image.open('images\\shield.png').tobytes(), (30, 30), 'RGBA')

    def run(self):
        stage=0
        player=0
        spellss=[]
        while self.running:
            events = self.selector.select(timeout=0.1)
            for key, mask in events:
                if key.data is None:
                    raise Exception('No data')
                else:
                    sock = key.fileobj
                    if stage==0:
                        data = sock.recv(1)
                        if data==enums.GameMessages.PLAYER1.value: player=0
                        elif data==enums.GameMessages.PLAYER2.value: player=1
                        elif data==enums.GameMessages.SPELL1.value: player=2
                        elif data==enums.GameMessages.SPELL2.value: player=3
                        elif data==enums.GameMessages.SPELL3.value: player=4
                        elif data==enums.GameMessages.END.value: self.game.end()
                        stage+=1
                    elif stage==1:
                        x=int.from_bytes(sock.recv(2),'big')
                        stage+=1
                    elif stage==2:
                        y=int.from_bytes(sock.recv(2),'big')
                        stage=0
                        if player==0:
                            self.game.player1.setPoz(x,y)
                        elif player==1:
                            self.game.player2.setPoz(x,y)
                            self.game.spellss=spellss
                            spellss=[]
                        elif player == 2:
                            spellss.append(spells.Ball(self.ball,x,y,0,0))
                        elif player == 3:
                            spellss.append(spells.Shield(self.shield,x,y,0,0))
                        elif player == 4:
                            pass
        self.selector.unregister(self.playerSocket)

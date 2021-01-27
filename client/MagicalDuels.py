import threading
import pygame
import pygame_gui
from client import Connector
from game import GameClient
import enums
import socket
from signs import Model
from PIL import Image,ImageDraw
import numpy as np
import pygame_gui.data

class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption(('MagicDuels'))
        self.manager=pygame_gui.UIManager(pygame.display.get_surface().get_size())
        self.running=True
        self.connector=Connector.Server_Connector()
        self.connector.connect()
        self.model=Model.Model()
        self.model.predict(Image.new('1', (64, 64)))
        self.model.load()


    def loop(self):
        nickname_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((500, 325), (280, 70)),text='Akceptuj', manager=self.manager)
        label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((500, 125), (280, 70)),text='Podaj swoj nick(max 15 znaków):', manager=self.manager)
        entry = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((500, 225), (280, 70)), manager=self.manager)
        clock = pygame.time.Clock()
        stage=0
        lobbies = []
        movex = 0
        movey = 0
        notpressed = True
        mouse = [0, 0]
        image = Image.new('1', (1280, 720))
        imdraw = ImageDraw.Draw(image)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN and stage==3 and not game.finished:
                    if event.key == pygame.K_a: movex=-1
                    if event.key == pygame.K_d: movex=1
                    if event.key == pygame.K_w: movey=-1
                    if event.key == pygame.K_s: movey=1
                    #if event.key == pygame.K_i: self.sender.send(enums.GameMessages.SPELL1.value)
                    #if event.key == pygame.K_o: self.sender.send(enums.GameMessages.SPELL2.value)
                    #if event.key == pygame.K_p: self.sender.send(enums.GameMessages.SPELL3.value)


                if event.type == pygame.MOUSEBUTTONUP and stage==3:
                    tt=threading.Thread(target=self.spell,args=(image.copy(),self))
                    tt.start()
                    image = Image.new('1', (1280, 720))
                    imdraw = ImageDraw.Draw(image)
                    notpressed = True


                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        if stage==0 and event.ui_element == nickname_button:
                            nick=entry.get_text()
                            if len(nick)>0 and len(nick)<=15:
                                self.connector.sendNickname(nick)
                                stage=1
                                self.manager.clear_and_reset()
                                createLobby = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 100), (180, 70)), text='Create Lobby',manager=self.manager)
                                refreshLobby = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 200), (180, 70)), text='Refresh lobbies',manager=self.manager)
                                lobbies = []
                                for i in range(self.connector.get_lobbies()):
                                    lobbies.append(pygame_gui.elements.UIButton(
                                        relative_rect=pygame.Rect((200, 100 + i * 100), (1060, 70)), text=str(i),
                                        manager=self.manager))
                        if stage == 1 and event.ui_element == createLobby:
                            self.connector.createLobby()
                            stage=2
                            self.manager.clear_and_reset()
                            pygame_gui.elements.UILabel(relative_rect=pygame.Rect((500, 325), (280, 70)),
                                                        text='Oczekiwanie na grę', manager=self.manager)
                            self.start = False
                            t = threading.Thread(target=self.waitForStart)
                            t.start()
                        if stage == 1 and event.ui_element == refreshLobby:
                            self.manager.clear_and_reset()
                            createLobby = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 100), (180, 70)), text='Create Lobby', manager=self.manager)
                            refreshLobby = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 200), (180, 70)),text='Refresh lobbies', manager=self.manager)
                            lobbies=[]
                            for i in range(self.connector.get_lobbies()):
                                lobbies.append(pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 100+i*100), (1060, 70)), text=str(i), manager=self.manager))

                        if stage == 1 and event.ui_element in lobbies:
                            self.connector.joinLobby(lobbies.index(event.ui_element))
                            stage=2
                            self.manager.clear_and_reset()
                            pygame_gui.elements.UILabel(relative_rect=pygame.Rect((500, 325), (280, 70)),
                                                        text='Oczekiwanie na grę', manager=self.manager)
                            self.start=False
                            t=threading.Thread(target=self.waitForStart)
                            t.start()


                self.manager.process_events(event)

            self.manager.update(clock.tick(60)/1000.0)

            self.window.fill((0, 0, 0))

            if stage==2 and self.start:
                stage=3
                self.manager.clear_and_reset()
                game=GameClient.Game(self.connector.sock)
            elif stage==3 and not game.finished:
                if pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    if notpressed:
                        notpressed = False
                        mouse[0] = pos[0]
                        mouse[1] = pos[1]
                    imdraw.line([(mouse[0], mouse[1]), (pos[0], pos[1])], 1, 9)
                    mouse[0] = pos[0]
                    mouse[1] = pos[1]
                if movex==0 and movey==-1: self.sender.send(enums.GameMessages.MOVEN.value)
                elif movex==0 and movey==1: self.sender.send(enums.GameMessages.MOVES.value)
                elif movex==1 and movey==0: self.sender.send(enums.GameMessages.MOVEE.value)
                elif movex==-1 and movey==0: self.sender.send(enums.GameMessages.MOVEW.value)
                elif movex==1 and movey==-1: self.sender.send(enums.GameMessages.MOVENE.value)
                elif movex==-1 and movey==-1: self.sender.send(enums.GameMessages.MOVENW.value)
                elif movex==1 and movey==1: self.sender.send(enums.GameMessages.MOVESE.value)
                elif movex==-1 and movey==1: self.sender.send(enums.GameMessages.MOVESW.value)
                game.draw(self.window)
                imagee=pygame.image.frombuffer(image.convert('RGB').tobytes(), (1280, 720), 'RGB')
                imagee.set_colorkey(0)
                self.window.blit(imagee, (0, 0))
                movex = 0
                movey = 0
            if stage==3 and game.finished:
                createLobby = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 100), (180, 70)),
                                                           text='Create Lobby', manager=self.manager)
                refreshLobby = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 200), (180, 70)),
                                                            text='Refresh lobbies', manager=self.manager)
                lobbies = []
                for i in range(self.connector.get_lobbies()):
                    lobbies.append(pygame_gui.elements.UIButton(
                        relative_rect=pygame.Rect((200, 100 + i * 100), (1060, 70)), text=str(i),
                        manager=self.manager))
                stage=1

            self.manager.draw_ui(self.window)

            pygame.display.flip()

        self.connector.deconnect()

    def waitForStart(self):
        sock=self.connector.sock
        data=sock.recv(1)
        if data!=enums.ConnectionMessages.PORT.value: raise Exception('Unknown data')
        port=int.from_bytes(sock.recv(2),'big')
        self.sender=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender.connect((self.connector.serverIp,port))
        self.start=True

    def spell(self,image,game):
        image = image.crop(image.getbbox()).resize((64, 64))
        ret = self.model.predict(np.array(image, np.float))
        if ret == 0:
            game.sender.send(enums.GameMessages.SPELL3.value)
        elif ret == 1:
            game.sender.send(enums.GameMessages.SPELL1.value)
        elif ret == 2:
            game.sender.send(enums.GameMessages.SPELL2.value)






game=Game()
game.loop()

import pygame
from PIL import Image,ImageDraw
import os
from signs import Model
import numpy as np
import matplotlib.pyplot as plt

def PrepareImages():
    pygame.init()
    window = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(('Preparation'))
    clock = pygame.time.Clock()
    image = Image.new('1', (1280, 720))
    imdraw = ImageDraw.Draw(image)
    running=True
    notpressed=True
    mouse=[0,0]

    liczba=0
    while str(liczba)+'.jpeg' in os.listdir('drawn'):
        liczba+=1

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.MOUSEBUTTONUP:
                image = image.crop(image.getbbox()).resize((64, 64))
                image.save('drawn\\o'+str(liczba) + '.jpeg')
                liczba+=1
                image = Image.new('1', (1280, 720))
                imdraw = ImageDraw.Draw(image)
                notpressed = True

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if notpressed:
                notpressed = False
                mouse[0] = pos[0]
                mouse[1] = pos[1]
            imdraw.line([(mouse[0], mouse[1]), (pos[0], pos[1])], 1, 9)
            mouse[0] = pos[0]
            mouse[1] = pos[1]

        window.fill((0, 0, 0))

        window.blit(pygame.image.frombuffer(image.convert('RGB').tobytes(), (1280, 720), 'RGB'), (0, 0))
        pygame.display.flip()
        clock.tick(60)

def TestPredict():
    pygame.init()
    window = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(('Preparation'))
    clock = pygame.time.Clock()
    image = Image.new('1', (1280, 720))
    imdraw = ImageDraw.Draw(image)
    running=True
    notpressed=True
    mouse=[0,0]
    model = Model.Model()
    model.load()

    liczba=0
    while str(liczba)+'.jpeg' in os.listdir('drawn'):
        liczba+=1
    print('ready')
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
            if event.type == pygame.MOUSEBUTTONUP:
                image = image.crop(image.getbbox()).resize((64, 64))
                #image.save('drawn\\'+str(liczba) + '.jpeg')
                ret=model.predict(np.array(image,np.float))
                if ret==0: print('z')
                elif ret==1: print('v')
                elif ret==2: print('o')
                liczba+=1
                image = Image.new('1', (1280, 720))
                imdraw = ImageDraw.Draw(image)
                notpressed = True

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            if notpressed:
                notpressed = False
                mouse[0] = pos[0]
                mouse[1] = pos[1]
            imdraw.line([(mouse[0], mouse[1]), (pos[0], pos[1])], 1, 9)
            mouse[0] = pos[0]
            mouse[1] = pos[1]

        window.fill((0, 0, 0))

        window.blit(pygame.image.frombuffer(image.convert('RGB').tobytes(), (1280, 720), 'RGB'), (0, 0))
        pygame.display.flip()
        clock.tick(60)

def learning():
    inputt=[]
    expected=[]
    temp=os.listdir('drawn')
    np.random.shuffle(temp)
    for i in temp:
        if i.startswith('z'):
            inputt.append(np.reshape(np.array(Image.open('drawn\\'+i).convert('1'),np.float),(64,64,1)))
            expected.append([1.0,0.0,0.0])
        elif i.startswith('v'):
            inputt.append(np.reshape(np.array(Image.open('drawn\\'+i).convert('1'),np.float),(64,64,1)))
            expected.append([0.0, 1.0, 0.0])
        elif i.startswith('o'):
            inputt.append(np.reshape(np.array(Image.open('drawn\\'+i).convert('1'),np.float),(64,64,1)))
            expected.append([0.0, 0.0, 1.0])
    model = Model.Model()
    loss=[]
    valloss=[]
    accuracy=[]
    valaccuracy=[]
    plt.rcParams["figure.figsize"] = (10,8)
    while valaccuracy==[] or valaccuracy[-1]<0.95:
        hist=model.learn(inputt,expected).history
        loss+=hist['loss']
        valloss+=hist['val_loss']
        accuracy+=hist['accuracy']
        valaccuracy+=hist['val_accuracy']
        plt.subplot(2, 1, 1)
        plt.cla()
        plt.plot(range(1, len(loss) + 1), loss)
        plt.plot(range(1, len(valloss) + 1), valloss)
        plt.title('signs loss')
        plt.xlabel('epoch')
        plt.ylabel('loss')
        plt.legend(['train', 'validation'])
        plt.subplot(2, 1, 2)
        plt.cla()
        plt.plot(range(1, len(accuracy) + 1), accuracy)
        plt.plot(range(1, len(valaccuracy) + 1), valaccuracy)
        plt.title('signs accuracy')
        plt.xlabel('epoch')
        plt.ylabel('accuracy')
        plt.legend(['train', 'validation'])
        plt.pause(0.01)
    plt.subplots_adjust(left=0.12,
                        bottom=0.06,
                        right=0.9,
                        top=0.97,
                        wspace=0.2,
                        hspace=0.26)
    plt.savefig('signs.jpg')
    plt.show()
    model.save()


TestPredict()
#learning()
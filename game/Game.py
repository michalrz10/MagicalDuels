import pygame

class GameObject:
    def __init__(self,image=None,x=0,y=0):
        self.image=image
        self.x=x
        self.y=y
        self.crash=False

    def draw(self, window):
        window.blit(self.image, (self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2))

class Mage(GameObject):
    def __init__(self,image=None,x=0,y=0):
        GameObject.__init__(self,image,x,y)

    def moveTo(self,ymove,xmove):
        self.x+=xmove
        self.y+=ymove

    def setPoz(self,x,y):
        self.x=x
        self.y=y
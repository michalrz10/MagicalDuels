from game.Game import GameObject

class Spell(GameObject):
    def __init__(self,image=None,x=0,y=0,xmove=0,ymove=0):
        GameObject.__init__(self,image,x,y)
        self.xmove=xmove
        self.ymove=ymove


    def iteration(self):
        self.x+=self.xmove
        self.y+=self.ymove

    def collision(self,go:GameObject):
        pass

class Shield(Spell):
    def __init__(self,image=None,x=0,y=0,xmove=0,ymove=0):
        Spell.__init__(self, image, x, y,xmove,ymove)
        self.name='shield'

    def collision(self,go:GameObject):
        go.crash=True
        self.crash=True


class Ball(Spell):
    def __init__(self,image=None,x=0,y=0,xmove=0,ymove=0):
        Spell.__init__(self, image, x, y,xmove,ymove)
        self.name = 'ball'

    def collision(self,go:GameObject):
        go.crash=True

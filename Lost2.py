import pygame, copy, os
from math import sqrt
from random import randint
pygame.init()

clock = pygame.time.Clock()
FPS = 30

cellSize = 20
memory = False

screenWidth = 20*cellSize
screenHeight = 20*cellSize
screen = pygame.display.set_mode((screenWidth, screenHeight))

pygame.display.set_caption("Lost")
icon = pygame.transform.scale(pygame.image.load("Lost Icon.png"), (32, 32))
pygame.display.set_icon(icon)

black = (50,50,50)
grey = (128,128,128)
white = (205,205,205)

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

yellow = (255,255,0)
turquoise = (0,255,255)
magenta = (255,0,255)

orange = (255, 128, 0)
pink = (255, 0, 128)
iceblue = (0, 128, 255)

if cellSize > 5:
    size = cellSize-5
else:
    size = 5
font = pygame.font.Font("FreeSansBold.ttf", size)
sfont = pygame.font.Font("FreeSansBold.ttf", 9)

def text(mes, colour, hs, vs, x, y, bck=False, fnt=font):
    message = fnt.render(mes, True, colour)
    w, h = fnt.size(mes)
    
    rect = pygame.Rect(0, 0, w, h)
    SetPosition(rect, hs, vs, x, y)
    if rect.left < 0:
        rect.left = 0
    if rect.right > screenWidth:
        rect.right = screenWidth

    if rect.top < 0:
        rect.top = 0
    if rect.bottom > screenHeight:
        rect.bottom = screenHeight

    if bck:
        opocol = []
        for c in colour:
            opocol.append(255-c)
        pygame.draw.rect(screen, opocol, rect)
    screen.blit(message, rect.topleft)

def SetPosition(rect, hs, vs, x, y):
    if hs == "left":
        rect.left = x
    elif hs == "right":
        rect.right = x
    else:
        rect.centerx = x

    if vs == "top":
        rect.top = y
    elif vs == "bottom":
        rect.bottom = y
    else:
        rect.centery = y

gamelayout0 = pygame.transform.scale(pygame.image.load("GameLayout0Mimic.png"), (screenWidth, screenHeight))
gamelayout1 = pygame.image.load("GameLayout1.png")
gamelayout2 = pygame.image.load("GameLayout2Mimic.png")
fill = white
quest = ""
quest2 = ""

def dist(obj1, obj2):
    a = abs(obj1.rect.x-obj2.rect.x)
    b = abs(obj1.rect.y-obj2.rect.y)

    c = sqrt(a**2+b**2)
    return c

Objects = []
teleObjects = []

treasureNum = 0
torchNum = 0

switch = True
def Switch(o):
    global switch, control, torchNum
    switch = False

    sr = control.sightRange
    control = o
    control.sightRange = sr

    count = 0
    for o in range(len(Objects)):
        obj = Objects[count]
        if type(obj) == Torch:
            Objects.remove(obj)
            torchNum += 1
        else:
            count += 1

    if type(control) == Player:
        for oo in Objects:
            if type(oo) == PinkBlock:
                if not oo.control:
                    oo.solid = True
    elif type(control) == PinkBlock:
        control.control = True
        for oo in Objects:
            if type(oo) == PinkBlock:
                oo.solid = False

class Player:
    sightNum = 1
    def __init__(self, x, y, col=black, opocol=white):
        Objects.append(self)
        self.solid = False

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.colour = col
        self.normcol = col
        self.opocolour = opocol

        self.control = True
        self.sightRange = 1

    def checkCollide(self):
        for o in Objects:
            if o == self:
                continue

            if hasattr(o, "rect"):
                if self.rect.colliderect(o.rect):
                    return True, o
        count = 0
        for o in Objects:
            obj = Objects[count]
            if type(obj) == MemoryBlock:
                if obj.used:
                    Objects.remove(obj)
                else:
                    count += 1
            else:
                count += 1
        return False

    def checkOutside(self):
        if self.rect.left < 0:
            return True
        if self.rect.right > screenWidth:
            return True
        if self.rect.top < 0:
            return True
        if self.rect.bottom > screenHeight:
            return True

    def Move(self, x, y):
        self.rect.x += x
        self.rect.y += y

        global switch
        if not switch:
            switch = True

        if self.checkOutside():
            self.Move(-x, -y)

        global memory
        if self.checkCollide():
            obj = self.checkCollide()[1]
            
            if type(self) == Player and hasattr(obj, "solid") or type(self) == PinkBlock and hasattr(obj, "solid") and type(obj) != Player:
                if obj.solid:
                    self.Move(-x, -y)

            global quest, treasureNum
            if type(obj) == NPC:
                if obj.name == "Rial":
                    if quest == "Speak to woman":
                        Speech("You took your time", obj)
                        def func():
                            for o in Objects:
                                if type(o) == Player:
                                    o.sightRange += 1
                        Speech("I think you need this...", obj, func)
                        Speech("You clearly have no idea where you are going", obj)
                        Speech("And it's starting to annoy me", obj)
                        Speech("Get some yellow treasure and bring it back here", obj)
                        
                        MemoryBlock(18, 18)
                        MemoryBlock(19, 18)
                        MemoryBlock(18, 19)

                        if treasureNum > 0:
                            Speech("Oh it looks like you've snatched some already", obj)
                            Speech("You can't keep that you know", obj)
                            def func():
                                global treasureNum
                                treasureNum -= 1
                            Speech("I'll take it for you", obj, func)
                            Speech("...What?", obj)
                            Speech("You want something for that treasure that wasn't yours?", obj)
                            def func():
                                global torchNum
                                torchNum += 1
                            Speech("Here take this but don't expect much else", obj, func)
                            Speech("And I'm being kind", obj)
                            Speech("Torches have great uses you know", obj)
                            Speech("I don't know why I even gave it to you", obj)
                            Speech("Press enter to use/put away a torch")
                        else:
                            Speech("And don't take forever", obj)
                            Speech("Press enter to collect treasure")
                            Speech("(You need to be on top of it first)")
                        quest = "Collect treasure"
                        
                    elif quest == "Collect treasure":
                        if treasureNum > 0:
                            count = 0
                            for o in Objects:
                                if type(o) == Treasure:
                                    count += 1
                            for t in range(treasureNum):
                                def func():
                                    global treasureNum, torchNum
                                    treasureNum -= 1
                                    control.sightRange += 1
                                    torchNum += 1
                                if count > 0:
                                    Speech("What are you doing standing here?", obj)
                                    Speech("There's still "+str(count)+" more to go", obj, func)
                                    if count == 3:
                                        Speech("Here have a torch, it might be helpful", obj)
                                        Speech("Press enter to use/put away a torch")
                                    if count == 1:
                                        Speech("3 torches can be very useful you know", obj)
                                        Speech("Place them around things to activate them", obj)
                                else:
                                    if type(self) == Player:
                                        Speech("What are you-", obj)
                                        Speech("Oh there's none left", obj, func)
                                        def mem(m):
                                            global memory
                                            memory = m
                                        Speech("That only means one thing...", obj, lambda:mem(True))
                                        Speech("Go", FindNPC("Tuto"))
                                        Speech("The teleport pod... Purple block", FindNPC("Tuto"), lambda:mem(False))
                                        Speech("It requires you be a pink block-", obj)
                                        Speech("Oh you're not pink... Don't worry then", obj)
                                        Speech("Finally... You can leave", obj, lambda:mem(True))
                                        Speech("The world is", FindNPC("Tuto"), lambda:mem(False))
                                        Speech("Boring and you're making it more boring", obj)
                                        Speech("Please do not bore me any longer", obj)
                            
                                        MemoryBlock(18, 18)
                                        MemoryBlock(19, 18)
                                        MemoryBlock(18, 19)
                                        quest = "Teleport"
                                    else:
                                        Speech("Woah I've never seen a pink block before", obj)
                                        Speech("I mean... What are you doing here?", obj)
                                        Speech("I don't have any tasks for you", obj)
                                        Speech("Start with something small and stay out of my way", obj)

            if type(obj) == MemoryBlock:
                memory = True
                obj.used = True
                
                global quest2
                if quest2 == "":
                    Speech("Press any key to get rid off me", FindNPC("Tuto"))
                    quest2 = "Speak to man"
                if quest == "Collect treasure" and quest2 == "Speak to man":
                    Speech("Try not to flood the world this time", FindNPC("Tuto"))
                    quest2 = "Ignore"
                if quest == "Teleport" and quest2 == "Ignore":
                    Speech("You have as much chance of leaving as I did here", FindNPC("Tuto"))
                    Speech("So good luck with that", FindNPC("Tuto"))
                    quest2 = "okay"
        else:
            if memory:
                memory = False
                        
    def Input(self, e):
        global control, quest, torchNum
        if control == self:
            if e.type == pygame.KEYDOWN:
                if len(s.mes) == 0:
                    if e.key == pygame.K_a:
                        self.Move(-cellSize, 0)
                    if e.key == pygame.K_d:
                        self.Move(cellSize, 0)

                    if e.key == pygame.K_w:
                        self.Move(0, -cellSize)
                    if e.key == pygame.K_s:
                        self.Move(0, cellSize)

                    if e.key == pygame.K_RETURN:
                        place = True
                        for o in Objects:
                            if o == self:
                                continue
                            if hasattr(o, "rect"):
                                if self.rect.colliderect(o.rect):
                                    place = False
                                    if type(o) == Torch:
                                        Objects.remove(o)
                                        torchNum += 1
                                        break
                        if place and torchNum > 0:
                            global switch
                            if switch:
                                Torch(self.rect.x, self.rect.y)
                                torchNum -= 1

                            for o in Objects:
                                if o == self:
                                    continue
                                if type(o) == PinkBlock or type(o) == Player:
                                    go = False
                                    if switch:
                                        for oo in Objects:
                                            if type(oo) == Torch:
                                                if dist(o, oo) == cellSize:
                                                    go = True
                                    if go and switch:
                                        if o.control:
                                            Switch(o)
                                            break
                        else:              
                            for o in Objects:
                                if hasattr(o, "rect"):
                                    if self.rect.colliderect(o.rect):
                                        if type(o) == Treasure:
                                            Objects.remove(o)
                                            global treasureNum
                                            treasureNum += 1
                                
    def Update(self):
        if self.solid:
            pygame.draw.rect(screen, self.colour, self.rect)
        else:
            pygame.draw.rect(screen, self.colour, self.rect, 1)

        if control == self:
            if treasureNum > 0:
                text(str(treasureNum), yellow, "left", "centery",
                     self.rect.right+4, self.rect.top, fnt=sfont)
            if torchNum > 0:
                text(str(torchNum), orange, "left", "centery",
                     self.rect.right+4, self.rect.bottom, fnt=sfont)

class NPC:
    def __init__(self, name, col, x, y):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.colour = col
        self.name = name

    def Update(self):
        if self.colour != None:
            pygame.draw.rect(screen, self.colour, self.rect, 1)

def FindNPC(name):
    for o in Objects:
        if type(o) == NPC:
            if o.name == name:
                return o

class SpeechBox:
    class Message:
        def __init__(self, owner, mes, obj=None, func=None, spd=0):
            owner.mes.append(self)
            
            self.mes = mes
            self.obj = obj
            
            self.func = func
            self.spd = spd
            
    def __init__(self):
        Objects.append(self)
        self.mes = []

        self.mmsg = None
        self.cmsg = ""
        self.opocolour = (255-fill[0], 255-fill[1], 255-fill[2])

        self.maxCount = 2
        self.count = 0
        self.speed = False

    def Mes(self, mes, obj=None, func=None, spd=1):
        if obj == FindNPC("Tuto"):
            spd = 5
        self.Message(self, mes, obj, func, spd)

    def Input(self, e):
        if e.type == pygame.KEYDOWN:
            if len(self.mes) > 0:
                if self.mes[0].spd == 1:
                    self.speed = True
            
        if e.type == pygame.KEYUP:
            if len(self.mes) > 0:
                if self.cmsg == self.mmsg:
                    if self.mes[0].func != None:
                        self.mes[0].func()
                        
                    del self.mes[0]
                    self.mmsg = None
                else:
                    self.speed = False

    def Update(self):
        if len(self.mes) > 0:
            if self.mmsg == None:
                self.mmsg = self.mes[0].mes
                self.cmsg = ""
                self.maxCount = self.mes[0].spd
                if self.maxCount > 1:
                    self.speed = False

            if self.cmsg != self.mmsg:
                if self.count >= self.maxCount:
                    self.cmsg += self.mmsg[len(self.cmsg)]
                    self.count = 0
                else:
                    if self.speed:
                        amount = self.maxCount
                    else:
                        amount = 1
                    self.count += amount

            if self.mes[0].obj != None:
                hs, vs = "centerx", "bottom"
                x, y = self.mes[0].obj.rect.centerx, self.mes[0].obj.rect.top-4
            else:
                hs, vs = "centerx", "centery"
                x, y = screenWidth*.5, 4

            text(self.cmsg, self.opocolour, hs, vs, x, y, bck=True)

class Wall:
    sightNum = 1
    def __init__(self, x, y, w=1, h=1):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x, y, w*cellSize, h*cellSize)
        self.colour = grey

    def Update(self):
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class Treasure:
    sightNum = 1
    def __init__(self, x, y):
        Objects.append(self)
        self.solid = False
        self.save = True

        self.rect = pygame.Rect(x, y, cellSize, cellSize)
        self.colour = yellow

    def Update(self):
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class Torch:
    def __init__(self, x, y):
        Objects.append(self)
        self.solid = False

        self.rect = pygame.Rect(x, y, cellSize, cellSize)
        self.colour = orange

        self.sightRange = 0

    def Update(self):
        self.sightRange = control.sightRange+1
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class PinkBlock:
    sightNum = 1
    def __init__(self, x, y):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x, y, cellSize, cellSize)
        self.colour = pink

        self.sightRange = 1
        self.control = False

    def checkOutside(self):
        return Player.checkOutside(self)
        
    def checkCollide(self):
        return Player.checkCollide(self)

    def Move(self, x, y):
        Player.Move(self, x, y)

    def Input(self, e):
        Player.Input(self, e)

    def Update(self):
        Player.Update(self)

        if not self.control:
            ts = []
            for o in Objects:
                if type(o) == Torch:
                    if dist(self, o) == cellSize:
                        ts.append(o)
            if len(ts) >= 3:
                Switch(self)

class Ice:
    sightNum = 1
    def __init__(self, x, y):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x, y, cellSize, cellSize)
        self.colour = iceblue

    def Update(self):
        solid = True
        for o in Objects:
            if type(o) == Torch:
                if dist(self, o) <= cellSize:
                    solid = False
        self.solid = solid

        if self.solid:
            fill = 0
        else:
            fill = 1
        pygame.draw.rect(screen, self.colour, self.rect, fill)

class TeleportPod:
    sightNum = 1
    def __init__(self, x, y):
        Objects.append(self)
        self.solid = False
        self.save = True

        self.rect = pygame.Rect(x, y, cellSize, cellSize)
        self.rect2 = pygame.Rect(0, 0, 0, 0)
        self.colour = magenta

        self.player = None
        self.maxPow = FPS*5
        self.pow = 0

        self.maxCount = 3
        self.count = 0

    def Teleport(self):
        global fill
        if self.count >= self.maxCount:
            if Objects[0] == self:
                if len(Objects) == 1:
                    Objects.remove(self)
                    fill = yellow
                    class Rect:
                        def __init__(self, x, y, col):
                            Objects.append(self)
                            self.rect = pygame.Rect(x, y, cellSize, cellSize)
                            self.col = col
                        def Update(self):
                            pygame.draw.rect(screen, self.col, self.rect, 1)
                    p = Player(9, 2, col=pink)
                    p.rect.size = (cellSize*2, cellSize*2)
                    p.colour = pink
                    NPC("Harry", None, 8, 9)
                    NPC("Zara", None, 11, 9)
                    for w in range(screenWidth):
                        if w % cellSize != 0 or w == screenWidth:
                            continue
                        for h in range(screenHeight):
                            if h % cellSize != 0 or h == screenHeight:
                                continue
                            col = gamelayout2.get_at((w, h))
                            if col != yellow and col != pink:
                                Rect(w, h, col)
                    def func():
                        def f():
                            pygame.quit()
                            quit()
                        Speech("Chapter 2 complete", func=f)
                    s = SpeechBox()
                    Speech = s.Mes
                    Speech("Look mummy! It's a giant!", FindNPC("Harry"), func)
            else:
                Objects.remove(Objects[0])
            self.count = 0
        else:
            self.count += 1

    def Update(self):
        if self.rect.colliderect(control.rect):
            if self.pow < self.maxPow:
                self.pow += 1
                if self.pow == self.maxPow:
                    control.sightRange = screenWidth*2
                    Objects.remove(control)
                    Objects.remove(self)
                    Objects.append(control)
                    Objects.append(self)
            self.rect2.h = (self.pow/self.maxPow)*self.rect.h
            self.rect2.bottom = self.rect.bottom
            self.rect2.w = 4
            self.rect2.left = self.rect.right+2
        else:
            self.pow = 0

        if self.pow == self.maxPow:
            self.Teleport()

        pygame.draw.rect(screen, self.colour, self.rect2)
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class MemoryBlock:
    def __init__(self, x, y, count=1):
        Objects.append(self)
        self.solid = False

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.count = count
        self.used = False

def checkVisible(self):
    lights = [control]
    for o in Objects:
        if type(o) == Torch:
            lights.append(o)

    true = False
    for l in lights:
        if l.sightRange >= self.sightNum:
            if dist(self, l) <= l.sightRange*cellSize:
                true = True
    return true

control = Player(4, 4)
s = SpeechBox()
s.gui = True
Speech = s.Mes

for o in Objects:
    o.save = True

def Room(rm=None):
    count = 0
    for o in range(len(Objects)):
        obj = Objects[0+count]
        if not hasattr(obj, "save"):
            Objects.remove(obj)
        else:
            count += 1

    global room, pastroom
    if rm == None:
        rm = room
    else:
        room = rm
        
    global quest, fill
    if room == 1:
        fill = white
        global control
        for o in Objects:
            if type(o) == Player:
                control = o
                break
        for w in range(screenWidth):
            if w % cellSize != 0 or w >= screenWidth:
                continue
            for h in range(screenHeight):
                if h % cellSize != 0 or h >= screenHeight:
                    continue
                
                col = gamelayout1.get_at((w//cellSize, h//cellSize))
                if col == grey:
                    Wall(w, h)
                if col == yellow:
                    Treasure(w, h)
                if col == pink:
                    PinkBlock(w, h)
                if col == iceblue:
                    Ice(w, h)
                if col == magenta:
                    TeleportPod(w, h)
                if col == orange:
                    MemoryBlock(w//cellSize, h//cellSize)
        NPC("Tuto", None, 19, 19)
        NPC("Rial", black, 15, 15)

    if quest == "":
        Speech("Press any key", obj=FindNPC("Rial"))
        Speech("Now make your way here", obj=FindNPC("Rial"))
        quest = "Speak to woman"

    pastroom = room
    if room != rm:
        room = rm

    count = 0
    saves = []
    for o in Objects:
        obj = Objects[0+count]
        if hasattr(obj, "save"):
            Objects.remove(obj)
            saves.append(obj)
        else:
            count += 1
    for s in saves:
        Objects.append(s)

pastroom = None
room = 1

lostHomepage = pygame.image.load("Lost Homepage.png")
def StartScreen():
    Objects = []
    class Button:
        def __init__(self, hs, vs, x, y, w, h, col1, func, text="", col2=None, fnt=font):
            Objects.append(self)

            self.rect = pygame.Rect(x, y, w*cellSize, h*cellSize)
            self.text = text
            self.fnt = fnt

            if self.text != "":
                size = self.fnt.size(self.text)
                self.rect.size = size
            SetPosition(self.rect, hs, vs, x, y)

            self.col1 = col1
            self.col2 = col2

            self.func = func
            self.select = False

        def Input(self, e):
            if e.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if self.select:
                        self.func()
            
        def Update(self):
            mousex, mousey = pygame.mouse.get_pos()
            mouseRect = pygame.Rect(mousex, mousey, 1, 1)
            if self.rect.colliderect(mouseRect):
                self.select = True
            else:
                self.select = False

            if self.select:
                pygame.draw.rect(screen, self.col1, self.rect)
                if self.text != "":
                    text(self.text, self.col2, "centerx", "centery",
                         self.rect.centerx, self.rect.centery, self.fnt)
            else:
                pygame.draw.rect(screen, self.col1, self.rect, 1)
                if self.text != "":
                    text(self.text, self.col1, "centerx", "centery",
                         self.rect.centerx, self.rect.centery, self.fnt)
    StartScreen.loop = True
    def func():
        StartScreen.loop = False
        Room()
    global lostHomepage
    lostHomepage = pygame.transform.scale(lostHomepage, (screenWidth, screenHeight))
    Button("centerx", "centery", screenWidth*.5, screenHeight*.5, 0, 0, white, func, text="Start", col2=black, fnt=font)
    while StartScreen.loop:
        for e in pygame.event.get():
            for o in Objects:
                if hasattr(o, "Input"):
                    o.Input(e)
            if e.type == pygame.QUIT:
                loop = False
                pygame.quit()
                quit()

        screen.fill(black)
        screen.blit(lostHomepage, (0, 0))

        for o in Objects:
            if hasattr(o, "Update"):
                o.Update()

        clock.tick(FPS)
        pygame.display.update()
StartScreen()

gameloop = True
while gameloop:
    for e in pygame.event.get():
        for o in Objects:
            if hasattr(o, "Input"):
                o.Input(e)

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_p:
                pygame.image.save(screen, "ScreenShot.png")
                
        if e.type == pygame.QUIT:
            gameloop = False
            pygame.quit()

    if not gameloop:
        break

    screen.fill(fill)

    for i in range(2):
        for o in Objects:
            if i == 0 and not hasattr(o, "save") or i == 1 and hasattr(o, "save"):
                if hasattr(o, "Update"):
                    if hasattr(o, "sightNum"):
                        if checkVisible(o):
                            o.Update()
                    else:
                        o.Update()
    if memory:
        screen.blit(gamelayout0, (0, 0))
        for o in Objects:
            if type(o) == Player or type(o) == SpeechBox:
                o.colour = o.opocolour
                o.Update()
    else:
        for o in Objects:
            if type(o) == Player:
                o.colour = o.normcol

    clock.tick(FPS)
    pygame.display.update()

import pygame, copy, os
from math import sqrt
from random import randint
pygame.init()

clock = pygame.time.Clock()
FPS = 30

cellSize = 20

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

def func():
    loop = False
StartScreen()

gamelayout = pygame.image.load("GameLayout0.png")
fill = black
quest = ""

def dist(obj1, obj2):
    a = abs(obj1.rect.x-obj2.rect.x)
    b = abs(obj1.rect.y-obj2.rect.y)

    c = sqrt(a**2+b**2)
    return c

Objects = []
teleObjects = []

class Player:
    def __init__(self, x, y, col=white):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.colour = col
        self.normcol = col
        
        self.rect2 = pygame.Rect(self.rect)
        self.rect2.h = 0
        self.rect2.bottom = self.rect.bottom

        self.maxStam = 1
        self.stam = {
            "Normal":-1,
            }

        self.treasure = 0
        self.mystery = 0
        
        self.resetpos = self.rect.topleft
        self.homepos = self.rect.topleft

        self.identitys = ["Normal"]
        self.idennum = 0
        self.identity = self.identitys[self.idennum]

    def addPower(self, power, bar=True):
        self.identitys.append(power)
        if bar:
            self.stam[power] = self.maxStam
            self.restorePower()
        else:
            self.stam[power] = -1

    def restorePower(self):
        for s in self.stam:
            if self.stam[s] >= 0:
                self.stam[s] = self.maxStam

    def checkCollide(self):
        for o in Objects:
            if o == self:
                continue

            if hasattr(o, "rect"):
                if self.rect.colliderect(o.rect):
                    return True, o
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

    def Move(self, x, y, second=False):
        self.rect.x += x
        self.rect.y += y

        if self.checkOutside():
            if not second:
                self.Move(-x, -y, True)
            else:
                self.rect.topleft = self.homepos
        
        if self.checkCollide():
            obj = self.checkCollide()[1]

            go = True
            if type(obj) == Tree:
                go = False
            if type(obj) == Block:
                go = False
                
            if go:
                if hasattr(obj, "solid"):
                    if obj.solid:
                        if not second:
                            self.Move(-x, -y, True)
                        else:
                            self.rect.topleft = self.homepos
                    else:
                        if type(obj) == Timer:
                            Speech("Press Spacebar to make time go faster")
                            Speech("Once the time has filled...")
                            Speech("The world resets and your last (valid) position is saved")
                            Speech("Press G to teleport to it or H for a valid spawn reset")
                            obj.solid = True
                
                if type(obj) == NPC:
                    if obj.name == "Tuto":
                        self.homepos = self.rect.topleft
                        global quest, teleObjects
                        if self.mystery > 0:
                            if quest != "Collect a mystery block" and quest != "Collect another mystery block":
                                if self.mystery > 0:
                                    Speech(str(self.mystery)+"blocks for "+str(self.mystery)+" stamina upgrades", obj)
                                    if quest == "Find all mystery blocks":
                                        count = 0
                                        for o in Objects:
                                            if type(o) == MysteryBlock:
                                                count += 1
                                        if count > 0:
                                            Speech(str(count)+" to go!", obj)
                                    loop = self.mystery
                                    for i in range(loop):
                                        self.mystery -= 1
                                        self.maxStam += 1
                                    if quest == "Find all mystery blocks":
                                        count = 0
                                        for o in Objects:
                                            if type(o) == MysteryBlock:
                                                count += 1
                                        if count == 0:
                                            Speech("That's it... You've found them all...", obj)
                                            Speech("That only means one thing...", obj)
                                            Speech("Go", obj)
                                            Speech("The teleport pod... Purple block...", obj)
                                            Speech("It requires full stamina", obj)
                                            Speech("Press enter to give it all your energy", obj)
                                            Speech("Then the teleport sequence can begin...", obj)
                                            quest = "Teleport"
                                            Speech("Finally... Take purple power", obj)
                                            self.addPower("Teleport")
                                            teleObjects = []
                                            for o in Objects:
                                                if not hasattr(o, "save"):
                                                    teleObjects.append(o)
                                                if type(o) == Player:
                                                    o.resetpos = o.rect.topleft
                                                    o.homepos = o.rect.topleft
                                            Speech("The world is flooding and that's the only way out", obj)
                                            Speech("Please do not get swallowed by its current", obj)
                                            for o in Objects:
                                                if type(o) == Timer:
                                                    o.go = False
                                            for o in Objects:
                                                if type(o) == TeleportPod:
                                                    for oo in Objects:
                                                        if type(oo) == Player:
                                                            o.maxPow = oo.maxStam
                                else:
                                    Speech("Ohhh, you don't have any more blocks for me", obj)
                            else:
                                if quest == "Collect a mystery block":
                                    Speech("Well done, your first mystery block!", obj)
                                    Speech("Hope it didn't cause you too much trouble", obj)
                                    Speech("Now, a stamina upgrade as promised", obj)
                                    self.mystery -= 1
                                    self.maxStam += 1
                                    Speech("One more now!", obj)
                                    quest = "Collect another mystery block"
                                if quest == "Collect another mystery block" and self.mystery > 0:
                                    Speech("There you go! That's two collected!", obj)
                                    Speech("And another stamina upgrade", obj)
                                    loop = self.mystery
                                    for i in range(loop):
                                        self.mystery -= 1
                                        self.maxStam += 1
                                    Speech("Now that you have enough stamina, I think it's time...", obj)
                                    Speech("For...", obj)
                                    Speech("Your new power!!!", obj)
                                    Speech("Take green power! It allows you to cut down trees", obj)
                                    self.addPower("Tree")
                                    Speech("Or what I like to call... Green blocks", obj)
                                    Speech("Anyway, you should be able to get more of my treasure now!", obj)
                                    Speech("Come back to me when you run out of stamina", obj)
                                    quest = "Next treasure"
                        restore = False
                        for s in self.stam:
                            if self.stam[s] < self.maxStam and self.stam[s] >= 0:
                                restore = True
                        if restore:
                            for s in self.stam:
                                if self.stam[s] != -1:
                                    self.stam[s] = self.maxStam
                        
                        if quest == "Speak to man":
                            Speech("So you finally made it...", obj)
                            Speech("Welcome to-", obj)
                            Speech("Actually there's no point in introductions...", obj)
                            Speech("Go collect my treasure, it's yellow", obj)
                            Speech("Just like you'll be when you press Q or E", obj)
                            Speech("You must be that colour to collect it (and see it)", obj)
                            Speech("And press enter of course!", obj)

                            quest = "Collect treasure"
                            self.addPower("Treasure", False)
                        if quest == "Collect treasure":
                            if self.treasure > 0:
                                Speech("This is exactly the treasure I was looking for!", obj)
                                self.treasure -= 1
                                Speech("Now, I don't know if you've seen any turquoise blocks", obj)
                                Speech("(Partly because you don't say anything)", obj)
                                Speech("But they are very helpful to you as they can increase your stamina", obj)
                                Speech("You can only see them as your normal self I think", obj)
                                Speech("And if you bring them to me I will upgrade your stamina", obj)
                                Speech("Here take this. It makes you turquoise! The colour for...", obj)
                                Speech("You know...", obj)
                                Speech("Picking up turqouise blocks", obj)
                                Speech("Find at least 2 and return to me when you have them", obj)
                                quest = "Collect a mystery block"
                                Speech("And remember... 1) Can only find when in normal form", obj)
                                Speech("2) When found, go on top of block in mysterious form", obj)
                                Speech("and press the enter key to collect it", obj)
                                self.addPower("Mystery", False)
                        if quest == "Next treasure":
                            if self.treasure == 1:
                                self.treasure -= 1
                                Speech("Wow, you are growing up so fast...", obj)
                                Speech("It wasn't too long ago before you knew what not being 'normal' was", obj)
                                Speech("Now you've been, yellow, turquoise and green", obj)
                                Speech("And now you can be red too!", obj)
                                self.addPower("Block")
                                Speech("This is when you can push other red blocks around", obj)
                                Speech("They're inanimate so it's alright", obj)
                                Speech("Now... Venture forth for the last treasure!", obj)
                                quest = "Last treasure"
                        if quest == "Last treasure":
                            if self.treasure == 1:
                                self.treasure -= 1
                                Speech("I can't believe it...", obj)
                                Speech("There's no more treasure to collect", obj)
                                fin = True
                                for o in Objects:
                                    if type(o) == MysteryBlock:
                                        fin = False
                                        break
                                if fin:
                                    Speech("Or mystery blocks...", obj)
                                    Speech("That only means one thing...", obj)
                                    Speech("Go", obj)
                                    Speech("The teleport pod... Purple block...", obj)
                                    Speech("It requires full stamina", obj)
                                    Speech("Press enter to give it all your energy", obj)
                                    Speech("Then the teleport sequence can begin...", obj)
                                    quest = "Teleport"
                                    Speech("Finally... Take purple power", obj)
                                    self.addPower("Teleport")
                                    teleObjects = []
                                    for o in Objects:
                                        if not hasattr(o, "save"):
                                            teleObjects.append(o)
                                        if type(o) == Player:
                                            o.resetpos = o.rect.topleft
                                            o.homepos = o.rect.topleft
                                    Speech("The world is flooding and that's the only way out", obj)
                                    Speech("Please do not get swallowed by its current", obj)
                                    for o in Objects:
                                        if type(o) == Timer:
                                            o.go = False
                                else:
                                    Speech("But there are some more mysterious blocks", obj)
                                    count = 0
                                    for o in Objects:
                                        if type(o) == MysteryBlock:
                                            count += 1
                                    Speech(str(count)+" to be precise", obj)
                                    Speech("There's one last thing to do but it requires full stamina", obj)
                                    Speech("So please come back to me once you've found them all", obj)
                                    Speech("And make sure you look EVERYWHERE", obj)
                                    quest = "Find all mystery blocks"
                                    
                if type(obj) == Water:
                    if quest == "Teleport":
                        Room()
                                    
            else:
                if self.stam[self.identity] > 0:
                    if type(obj) == Tree:
                        if self.identity == "Tree":
                            Objects.remove(obj)
                            self.stam[self.identity] -= 1
                        else:
                            if not second:
                                self.Move(-x, -y, True)
                            else:
                                self.rect.topleft = self.homepos
                            
                    if type(obj) == Block:
                        if self.identity == "Block":
                            obj.Move(x, y)
                            if obj.checkCollide():
                                if not second:
                                    self.Move(-x, -y, True)
                                else:
                                    self.rect.topleft = self.homepos
                            else:
                                self.stam[self.identity] -= 1
                        else:
                            if not second:
                                self.Move(-x, -y, True)
                            else:
                                self.rect.topleft = self.homepos
                else:
                    if not second:
                        self.Move(-x, -y, True)
                    else:
                        self.rect.topleft = self.homepos
        else:
            if quest == "Teleport":
                for o in Objects:
                    if type(o) == Water:
                        if len(o.waters) == 0:
                            o.spread += 1

    def Input(self, e):
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

                if e.key == pygame.K_g:
                    self.rect.topleft = self.resetpos
                if e.key == pygame.K_h:
                    self.rect.topleft = self.homepos

                if e.key == pygame.K_RETURN:
                    for o in Objects:
                        if hasattr(o, "rect"):
                            if self.rect.colliderect(o.rect):
                                if type(o) == Treasure and self.identity == "Treasure":
                                    Objects.remove(o)
                                    self.treasure += 1
                                    Water(self.rect.x, self.rect.y)
                                if type(o) == MysteryBlock and self.identity == "Mystery":
                                    Objects.remove(o)
                                    self.mystery += 1

                if e.key == pygame.K_q:
                    if self.idennum > 0:
                        self.idennum -= 1
                    else:
                        self.idennum = len(self.identitys)-1
                    
                if e.key == pygame.K_e:
                    if self.idennum < len(self.identitys)-1:
                        self.idennum += 1
                    else:
                        self.idennum = 0
                                
    def Update(self):
        self.identity = self.identitys[self.idennum]

        if self.identity == "Normal":
            self.colour = self.normcol
        elif self.identity == "Tree":
            self.colour = green
        elif self.identity == "Block":
            self.colour = red
        elif self.identity == "Treasure":
            self.colour = yellow
        elif self.identity == "Mystery":
            self.colour = turquoise
        elif self.identity == "Teleport":
            self.colour = magenta

        self.rect2.h = (self.stam[self.identity]/self.maxStam)*self.rect.h
        self.rect2.bottomright = self.rect.bottomright
            
        if self.rect2.h > 0:
            pygame.draw.rect(screen, self.colour, self.rect2)
        pygame.draw.rect(screen, self.colour, self.rect, 1)

        if fill == black:
            resetRect = pygame.Rect(self.resetpos[0], self.resetpos[1],
                                    self.rect.w, self.rect.h)
            if not self.rect.colliderect(resetRect):
                pygame.draw.rect(screen, self.colour, resetRect)
                text("G", fill, "centerx", "centery", resetRect.centerx, resetRect.centery)

            homeRect = pygame.Rect(self.homepos[0], self.homepos[1],
                                    self.rect.w, self.rect.h)
            if not self.rect.colliderect(homeRect):
                pygame.draw.rect(screen, self.colour, homeRect)
                text("H", fill, "centerx", "centery", homeRect.centerx, homeRect.centery)

        if self.treasure > 0:
            text(str(self.treasure), yellow, "left", "centery",
                 self.rect.right+4, self.rect.top, fnt=sfont)
        if self.mystery > 0:
            text(str(self.mystery), turquoise, "left", "centery",
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
        pygame.draw.rect(screen, self.colour, self.rect, 1)

def FindNPC(name):
    for o in Objects:
        if type(o) == NPC:
            if o.name == name:
                return o

class Timer:
    def __init__(self):
        Objects.append(self)
        self.solid = False

        self.rect = pygame.Rect(9*cellSize, 9*cellSize,
                                2*cellSize, 2*cellSize)
        self.colour = white
        
        self.rect2 = pygame.Rect(self.rect)
        self.rect2.bottom = self.rect.bottom
        self.rect2.left = self.rect.left

        self.maxTime = FPS*60*1.5
        self.time = 0
        self.speed = False
        self.go = True

    def Input(self, e):
        if len(s.mes) == 0:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.speed = True

        if e.type == pygame.KEYUP:
            if e.key == pygame.K_SPACE:
                self.speed = False

    def Update(self):
        self.rect2.h = (self.time/self.maxTime)*self.rect.h
        self.rect2.bottom = self.rect.bottom

        pygame.draw.rect(screen, self.colour, self.rect2)
        pygame.draw.rect(screen, self.colour, self.rect, 1)

        if self.go:
            if self.speed:
                timeInc = self.maxTime/FPS
            else:
                timeInc = 1
            self.time += timeInc
            if self.time > self.maxTime:
                self.time = 0
                Room()

class SpeechBox:
    class Message:
        def __init__(self, owner, mes, obj=None, func=None):
            owner.mes.append(self)
            
            self.mes = mes
            self.obj = obj
            self.func = func
            
    def __init__(self):
        Objects.append(self)
        self.mes = []

        self.mmsg = None
        self.cmsg = ""

        self.maxCount = 2
        self.count = 0
        self.speed = False

    def Mes(self, mes, obj=None, func=None):
        self.Message(self, mes, obj, func)

    def Input(self, e):
        if e.type == pygame.KEYDOWN:
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

            opocol = []
            for f in fill:
                opocol.append(255-f)
            text(self.cmsg, opocol, hs, vs, x, y, bck=True)

class Wall:
    def __init__(self, x, y, w, h):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                w*cellSize, h*cellSize)
        self.colour = grey

    def Update(self):
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class Tree:
    def __init__(self, x, y, w, h):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                w*cellSize, h*cellSize)
        self.colour = green

    def Update(self):
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class Block:
    def __init__(self, x, y, w, h):
        Objects.append(self)
        self.solid = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                w*cellSize, h*cellSize)
        self.colour = red

    def checkCollide(self):
        for o in Objects:
            if o == self:
                continue

            if hasattr(o, "rect"):
                if self.rect.colliderect(o.rect):
                    if hasattr(o, "solid"):
                        if o.solid:
                            return True

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
        
        if self.checkCollide() or self.checkOutside():
            self.rect.x -= x
            self.rect.y -= y
        
    def Update(self):
        pygame.draw.rect(screen, self.colour, self.rect, 1)

class Water:
    def checkValid(self):
        for o in Objects:
            if o == self or type(o) == Player:
                continue
            if hasattr(o, "rect"):
                if self.rect.colliderect(o.rect):
                    Objects.remove(self)
                    if self.owner != None:
                        self.owner.waters.remove(self)
                    break
        if self in Objects:
            go = False
            if self.rect.left < 0:
                go = True
            if self.rect.right > screenWidth:
                go = True
            if self.rect.top < 0:
                go = True
            if self.rect.bottom > screenHeight:
                go = True

            if go:
                Objects.remove(self)
                if self.owner != None:
                    self.owner.waters.remove(self)
                    
        if self in Objects:
            if quest == "Teleport":
                teleFull = False
                found = False
                for o in Objects:
                    if type(o) == TeleportPod:
                        found = True
                        if o.pow == o.maxPow:
                            teleFull = True
                            break
                if not found or teleFull:      
                    Objects.remove(self)
                    if self.owner != None:
                        self.owner.waters.remove(self)
                
    def __init__(self, x, y, owner=None):
        Objects.append(self)
        self.solid = False

        self.waters = []
        self.owner = owner
        if self.owner != None:
            self.owner.waters.append(self)
            self.spread = owner.spread-1
        else:
            self.save = True
            self.spread = 6

        self.rect = pygame.Rect(x, y, cellSize, cellSize)
        self.colour = blue

        self.checkValid()

        self.maxCount = FPS*randint(1, 3)
        self.count = 0

    def Spread(self):
        Water(self.rect.x-cellSize, self.rect.y, self)
        Water(self.rect.right, self.rect.y, self)
        Water(self.rect.x, self.rect.y-cellSize, self)
        Water(self.rect.x, self.rect.bottom, self)
        
        if len(self.waters) > 0:
            self.spread = 0

    def Update(self):
        if not self.solid:
            solid = True
            for o in Objects:
                if o == self:
                    continue
                if hasattr(o, "rect"):
                    if self.rect.colliderect(o.rect):
                        solid = False
            self.solid = solid
        else:
            if self.spread > 0:
                if self.count >= self.maxCount:
                    self.Spread()
                    self.maxCount = FPS*randint(1, 3)
                    self.count = 0
                else:
                    self.count += 1
        pygame.draw.rect(screen, self.colour, self.rect)

class Treasure:
    def __init__(self, x, y):
        Objects.append(self)
        
        self.solid = False
        self.save = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.colour = yellow

    def Update(self):
        for o in Objects:
            if type(o) == Player:
                if o.identity == "Treasure":
                    pygame.draw.rect(screen, self.colour, self.rect, 1)

class MysteryBlock:
    def __init__(self, x, y):
        Objects.append(self)
        
        self.solid = False
        self.save = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.colour = turquoise

    def Update(self):
        for o in Objects:
            if type(o) == Player:
                if dist(self, o) == cellSize and o.identity == "Normal":
                    pygame.draw.rect(screen, self.colour, self.rect, 1)

class TeleportPod:
    def __init__(self, x, y):
        Objects.append(self)
        self.solid = False
        self.save = True

        self.rect = pygame.Rect(x*cellSize, y*cellSize,
                                cellSize, cellSize)
        self.rect2 = pygame.Rect(0, 0, 0, 0)
        self.colour = magenta

        self.player = None
        self.maxPow = 8
        self.pow = 0

        self.maxCount = 3
        self.count = 0

    def Teleport(self):
        if self.count >= self.maxCount:
            if Objects[0] == self:
                if len(Objects) > 1:
                    Objects.remove(Objects[1])
                else:
                    Objects.remove(Objects[0])
                    global fill
                    fill = white
                    p = Player(4, 4, black)
                    def func():
                        global Objects
                        Objects = []
                        def f():
                            StartScreen()
                        SpeechBox().Mes("Chapter 1 Complete", func=f)
                    obj = NPC("Rial", black, 15, 15)
                    SpeechBox().Mes("Press any key", obj, func=func)
            else:
                Objects.remove(Objects[0])
            self.count = 0
        else:
            self.count += 1

    def Input(self, e):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_RETURN:
                if self.player != None:
                    if self.player.identity == "Teleport" and self.player.stam[self.player.identity] > 0:
                        self.player.stam[self.player.identity] -= 1
                        self.pow += 1

    def Update(self):
        player = None
        for o in Objects:
            if type(o) == Player:
                if self.rect.colliderect(o.rect):
                    player = o
        self.player = player
        if self.player == None:
            if self.pow != 0 and self.pow != self.maxPow:
                self.pow = 0
        else:
            self.rect2.h = (self.pow/self.maxPow)*self.rect.h
            self.rect2.bottom = self.rect.bottom
            self.rect2.w = 4
            self.rect2.left = self.rect.right+2

        if self.pow == self.maxPow:
            self.Teleport()

        pygame.draw.rect(screen, self.colour, self.rect2)
        pygame.draw.rect(screen, self.colour, self.rect, 1)
        

Player(0, 0)
Timer().gui = True
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
            
    if rm == 1:
        global quest
        if quest != "Teleport":
            for w in range(20):
                for h in range(20):
                    col = gamelayout.get_at((w, h))

                    if col == grey:
                        Wall(w, h, 1, 1)
                    elif col == green:
                        Tree(w, h, 1, 1)
                    elif col == red:
                        Block(w, h, 1, 1)

                    if pastroom == None:
                        if col == yellow:
                            Treasure(w, h)
                        elif col == turquoise:
                            MysteryBlock(w, h)
                        elif col == magenta:
                            TeleportPod(w, h)

            NPC("Tuto", white, 19, 19)

            if quest == "":
                global FindNPC
                Speech("Hey! Press any key to get rid off this message!", obj=FindNPC("Tuto"))
                Speech("Wooo you pressed something!", obj=FindNPC("Tuto"))
                Speech("And again! You must be a natural!", obj=FindNPC("Tuto"))
                
                Speech("Don't worry you'll be able to play soon!", obj=FindNPC("Tuto"))
                Speech("Oh wait you don't know how to play yet!", obj=FindNPC("Tuto"))
                Speech("Use WASD and make your way to me!", obj=FindNPC("Tuto"))
                Speech("I'm down here where you're reading!", obj=FindNPC("Tuto"))
                Speech("And you're up there in the top left!", obj=FindNPC("Tuto"))
                quest = "Speak to man"
        else:
            for t in teleObjects:
                Objects.append(t)

    pastroom = room

    if room != rm:
        room = rm

    for o in Objects:
        if type(o) == Player:
            col = False
            for oo in Objects:
                if oo == o:
                    continue

                if hasattr(oo, "rect"):
                    if o.rect.colliderect(oo.rect):
                        if hasattr(oo, "solid"):
                            if oo.solid:
                                o.rect.topleft = o.resetpos
                                col = True
            if not col:
                o.resetpos = o.rect.topleft

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
        if type(s) == Water:
            s.spread = 11

pastroom = None
room = 1
Room()

gameloop = True
while gameloop:
    for e in pygame.event.get():
        for o in Objects:
            if hasattr(o, "Input"):
                o.Input(e)
                
        if e.type == pygame.QUIT:
            gameloop = False
            pygame.quit()

    if not gameloop:
        break

    screen.fill(fill)

    for o in Objects:
        if hasattr(o, "Update"):
            o.Update()

    clock.tick(FPS)
    pygame.display.update()

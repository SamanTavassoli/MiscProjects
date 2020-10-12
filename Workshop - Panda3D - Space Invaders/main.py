from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import TextNode, TransparencyAttrib
from panda3d.core import LPoint3, LVector3
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from random import randint, choice, random
from direct.interval.MetaInterval import Sequence
from direct.interval.FunctionInterval import Wait, Func
import sys
import random

ALIEN_SCALE = 1.5
SCREEN_X = 20       # Screen goes from -20 to 20 on X
SCREEN_Y = 15       # Screen goes from -15 to 15 on Y

open10pt = None
closed10pt = None
open20pt = None
closed20pt = None
open30pt = None
closed30pt = None
alienBlast = None
arrow1 = None
arrow2 = None
boltLeft = None
boltRight = None
bulletImg = None

moveAmmount = 1
hightDecrement = 1.5
moveDownFlag = False

keys = {"moveLeft": 0, "moveRight": 0}

def loadObject(tex=None, pos=LPoint3(0, 0), depth=55, scale=1, transparency=True):
    # Every object uses the plane model and is parented to the camera
    # so that it faces the screen.
    obj = loader.loadModel("models/plane")
    obj.reparentTo(camera)

    # Set the initial position and scale.
    obj.setPos(pos.getX(), depth, pos.getZ())
    obj.setScale(scale)

    # This tells Panda not to worry about the order that things are drawn in
    # (ie. disable Z-testing).  This prevents an effect known as Z-fighting.
    obj.setBin("unsorted", 0)
    obj.setDepthTest(False)

    if transparency:
        # Enable transparency blending.
        obj.setTransparency(TransparencyAttrib.MAlpha)

    if tex:
        # Load and set the requested texture.
        tex = loader.loadTexture("textures/" + tex)
        obj.setTexture(tex, 1)

    return obj


def loadTexture(tex=None):
    return loader.loadTexture("textures/"+tex)


class Alien(DirectObject.DirectObject):
    def __init__(self, position=LPoint3(0,0), value=0, open_image=None, close_image=None, scale=1.5):

        self.pts = value
        self.open_tex = open_image
        self.close_tex = close_image
        self.obj = loadObject(pos=position, scale=scale)
        self.obj.setTexture(self.open_tex, 1)
        self.open = True

        self.accept('move', self.move)
        self.accept('moveDown', self.moveDown)

    def move(self):
        global moveAmmount
        global moveDownFlag
        if self.open:
            self.obj.setTexture(self.close_tex, 1)
            self.open = False
        else:
            self.obj.setTexture(self.open_tex, 1)
            self.open = True
        pos = self.obj.getPos()
        pos.setX(pos.getX() + moveAmmount)
        self.obj.setPos(pos)
        if abs(pos.getX()) > (SCREEN_X - 2.5):
            moveDownFlag = True
        self.obj.setPos(pos)

    def moveDown(self):
        global hightDecrement
        pos = self.obj.getPos()
        pos.setZ(pos.getZ() - hightDecrement)
        self.obj.setPos(pos)

    def delete(self):
        self.ignore('move')
        self.ignore('moveDown')


class Alien10pt(Alien):
    def __init__(self, position=LPoint3(0,0)):
        global open10pt
        global closed10pt
        Alien.__init__(self, position, 10, open10pt, closed10pt)


class Alien20pt(Alien):
    def __init__(self, position=LPoint3(0,0)):
        global open20pt
        global closed20pt
        Alien.__init__(self, position, 20, open20pt, closed20pt)


class Alien30pt(Alien):
    def __init__(self, position=LPoint3(0,0)):
        global open30pt
        global closed30pt
        Alien.__init__(self, position, 30, open30pt, closed30pt)


class Ship(DirectObject.DirectObject):
    def __init__(self):
        self.obj = loadObject(scale=2.5, pos=LPoint3(0, 0, -12.5))
        self.shipTex = loadTexture("ship.png")
        self.explode1 = loadTexture("ship_explode_one.png")
        self.explode2 = loadTexture("ship_explode_two.png")
        self.obj.setTexture(self.shipTex, 1)
        self.speed = 6
        self.bullets = []
        self.lives = 3
        self.accept("space", self.fire)

    def updatePosition(self, dt):
        global keys
        diff = 0
        if keys["moveLeft"]:
            diff -= self.speed
        if keys["moveRight"]:
            diff += self.speed
        diff *= dt
        pos = self.obj.getPos()
        pos.setX(pos.getX() + diff)
        if abs(pos.getX()) < (SCREEN_X-1.6):
            self.obj.setPos(pos)

        for i in range(len(self.bullets)-1, -1, -1):  # i start at greatest index, end at 0, decrement by 1
            bulletPos = self.bullets[i].getPos()
            bulletPos.setZ(bulletPos.getZ() + 10 * dt)
            if bulletPos.getZ() < SCREEN_Y:
                self.bullets[i].setPos(bulletPos)
            else:
                self.bullets[i].removeNode()
                del self.bullets[i]

        messenger.send("updateAlienShotPositions", [dt])

    # Creates a bullet and adds it to the bullet list
    def fire(self):
        if len(self.bullets) < 2:
            global bulletImg
            pos = self.obj.getPos()
            pos.setZ(-11)
            bullet = loadObject(pos=pos)
            bullet.setTexture(bulletImg, 1)
            self.bullets.append(bullet)

    def die(self):
        delay = Wait(0.1)
        self.lives -= 1
        deathSequence = Sequence(
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.explode1, 1), delay, Func(self.obj.setTexture, self.explode2, 1), delay,
            Func(self.obj.setTexture, self.shipTex, 1), Func(messenger.send, "restartTasks"))
        deathSequence.start()

class AlienBullets(DirectObject.DirectObject):
    def __init__(self, position, image1, image2):
        self.image1 = image1
        self.image2 = image2
        self.obj = loadObject(pos=position)
        self.obj.setTexture(self.image1, 1)
        self.first = True
        self.accept("switchImage", self.switchImage)

    def switchImage(self):
        if self.first:
            self.obj.setTexture(self.image2, 1)
            self.first = False
        else:
            self.obj.setTexture(self.image1, 1)
            self.first = True

    def die(self):
        self.obj.removeNode()
        self.ignore("switchImage")

class Arrow(AlienBullets):
    def __init__(self, position):
        super(Arrow, self).__init__(position, arrow1, arrow2)

class Bolt(AlienBullets):
    def __init__(self, position):
        super(Bolt, self).__init__(position, boltLeft, boltRight)

class SpaceInvaders(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor((0, 0, 0, 1))
        # load the background
        self.bg = loadObject("Game_Background.png", pos=LPoint3(0,0,3), scale=146, depth=200, transparency=False)
        # load the shields
        self.blockers = []
        self.blockers.append(loadObject("blocker.png", pos=LPoint3(3.5, 0, -9.2), scale=3.7))
        self.blockers.append(loadObject("blocker.png", pos=LPoint3(-3.5, 0, -9.2), scale=3.7))
        self.blockers.append(loadObject("blocker.png", pos=LPoint3(11, 0, -9.2), scale=3.7))
        self.blockers.append(loadObject("blocker.png", pos=LPoint3(-11, 0, -9.2), scale=3.7))
        # create ship
        self.ship = Ship()
        # create the list of alien shots
        self.alien_shots = []
        # start listening to the keys
        self.accept("escape", sys.exit)
        self.accept("arrow_left",     self.setKey,  ["moveLeft", 1])
        self.accept("arrow_left-up",  self.setKey,  ["moveLeft", 0])
        self.accept("arrow_right",    self.setKey, ["moveRight", 1])
        self.accept("arrow_right-up", self.setKey, ["moveRight", 0])
        # list to
        self.accept("updateAlienShotPositions", self.updateAlienShotPositions)

        # load the repeated textures we need
        global open10pt
        open10pt = loadTexture("10pts_Open.png")
        global closed10pt 
        closed10pt = loadTexture("10pts_Closed.png")
        global open20pt 
        open20pt = loadTexture("20pts_Open.png")
        global closed20pt 
        closed20pt = loadTexture("20pts_Closed.png")
        global open30pt
        open30pt = loadTexture("30pts_Open.png")
        global closed30pt
        closed30pt = loadTexture("30pts_Closed.png")
        global alienBlast 
        alienBlast = loadTexture("alien_Blast.png")
        global arrow1
        arrow1 = loadTexture("arrow.png")
        global arrow2
        arrow2 = loadTexture("arrow_Second.png")
        global boltLeft
        boltLeft = loadTexture("bolt_Left.png")
        global boltRight
        boltRight = loadTexture("bolt_Right.png")
        global bulletImg
        bulletImg = loadTexture("bullet.png")

        self.spawnAliens()
        self.startTasks()

    def startTasks(self):
        self.gameTask = self.taskMgr.add(self.gameLoop, "gameLoop")
        self.moveTask = self.taskMgr.doMethodLater(0.5, self.moveAliens, "moveAliens")
        # start alien bullet image switching task
        self.alien_bullet_image_switching_task = self.taskMgr.doMethodLater(0.1, self.shotsSwitchImage, "imageSwitching")
        # start the alien shooting task
        self.alien_shooting_task = self.taskMgr.doMethodLater(0.5, self.alienShoot, "alienShoot")

    def spawnAliens(self):
        self.aliens = []
        leftmost = -17
        highest = 13
        for i in range(11):
            self.aliens.append([])
            self.aliens[i].append(Alien30pt(position=LPoint3(leftmost + 2.5 * i, 0, highest)))
            self.aliens[i].append(Alien20pt(position=LPoint3(leftmost + 2.5 * i, 0, highest - 2.5)))
            self.aliens[i].append(Alien20pt(position=LPoint3(leftmost + 2.5 * i, 0, highest - 5.0)))
            self.aliens[i].append(Alien10pt(position=LPoint3(leftmost + 2.5 * i, 0, highest - 7.5)))
            self.aliens[i].append(Alien10pt(position=LPoint3(leftmost + 2.5 * i, 0, highest - 10.0)))

    def shotsSwitchImage(self, task):
        self.messenger.send("switchImage")
        return Task.again

    def updateAlienShotPositions(self, dt):
        # run through the shots and move them by down by the appropriate amount
        for i in range(len(self.alien_shots) - 1, -1, -1):
            pos = self.alien_shots[i].obj.getPos()
            pos.setZ(pos.getZ() - 10*dt)
            if pos.getZ() > -SCREEN_Y:
                self.alien_shots[i].obj.setPos(pos)
            else:
                self.alien_shots[i].die()
                del self.alien_shots[i]


    def alienShoot(self, task):
        # pick a random column of aliens, spawn an alien bullet underneath it
        random_column = random.randint(0, len(self.aliens) - 1)
        last_alien_position = self.aliens[random_column][-1].obj.getPos()
        last_alien_position.setZ(last_alien_position.getZ() - 1)
        bolt_or_arrow = random.randint(0, 1)
        if bolt_or_arrow == 0:
            self.alien_shots.append(Arrow(position=last_alien_position))
        else:
            self.alien_shots.append(Bolt(position=last_alien_position))
        task.delayTime = random.random()*5  # 0 - 5s
        return Task.again

    def moveAliens(self, task):
        global moveDownFlag
        if not moveDownFlag:
            self.messenger.send('move')
        else:
            self.messenger.send('moveDown')
            global moveAmmount
            moveAmmount = -moveAmmount
            moveDownFlag = False
        return Task.again

    def setKey(self, key, value):
        # function wrapper for changing a value at a key in the key dictionary
        global keys
        keys[key] = value

    def gameLoop(self, task):
        dt = globalClock.getDt()
        self.ship.updatePosition(dt)

        # ----- collision detection
        # shields and bullets
        for i in range(len(self.ship.bullets) - 1, -1, -1):
            shot = self.ship.bullets[i]
            for j in range(len(self.blockers)):
                blocker = self.blockers[j]
                if (shot.getPos() - blocker.getPos()).lengthSquared() < (shot.getScale().getX() + blocker.getScale().getX() * 0.5) ** 2:
                    self.ship.bullets[i].removeNode()
                    del self.ship.bullets[i]
                    break

        for i in range(len(self.aliens) - 1, -1, -1):  # each alien column

            # lowest alien and shields (sys.exit() if collision)
            for j in range(len(self.blockers)):
                alien = self.aliens[i][-1].obj  # bottom alien
                blocker = self.blockers[j]
                if (alien.getPos() - blocker.getPos()).lengthSquared() < (alien.getScale().getX() + blocker.getScale().getX() * 0.5) ** 2:
                    sys.exit()

            # aliens and player bullets
            for s in range(len(self.aliens[i]) - 1, -1, -1):  # each alien row
                alien = self.aliens[i][s].obj
                for j in range(len(self.ship.bullets)):
                    bullet = self.ship.bullets[j]
                    if (bullet.getPos() - alien.getPos()).lengthSquared() < (
                            bullet.getScale().getX() + alien.getScale().getX() * 0.5) ** 2:
                        self.ship.bullets[j].removeNode()
                        del self.ship.bullets[j]
                        self.aliens[i][s].obj.removeNode()
                        self.aliens[i][s].delete()
                        del self.aliens[i][s]
                        break  # each bullet can only hit one thing

                if len(self.aliens[i]) == 0:  # remove column if there are no more aliens in that column
                    del self.aliens[i]

        for i in range(len(self.alien_shots) - 1, -1, -1):
            # alien shots and shields
            shot = self.alien_shots[i].obj
            next_shot = False
            for j in range(len(self.blockers)):
                blocker = self.blockers[j]
                if (shot.getPos() - blocker.getPos()).lengthSquared() < (
                        shot.getScale().getX() + blocker.getScale().getX() * 0.5) ** 2:
                    self.alien_shots[i].die()
                    del self.alien_shots[i]
                    next_shot = True
                    break  # each bullet can only hit blocker once

            if next_shot:  # only do further checks if there are shots left for efficiency
                continue

            # alien shots and player
            ship = self.ship.obj
            if (shot.getPos() - ship.getPos()).lengthSquared() < (
                        shot.getScale().getX() + ship.getScale().getX() * 0.5) ** 2:
                self.taskMgr.remove("gameLoop")
                self.taskMgr.remove("moveAliens")
                self.taskMgr.remove("imageSwitching")
                self.taskMgr.remove("alienShoot")
                self.alien_shots[i].die()
                del self.alien_shots[i]
                if self.ship.lives > 0:
                    self.acceptOnce("restartTasks", self.startTasks)  # received at the end of death sequence of ship.die()
                    self.ship.die()
                else:
                    self.ship.die()
                    sys.exit()

        # check if won
        if len(self.aliens) == 0:
            sys.exit()


        return Task.cont

demo = SpaceInvaders()
demo.run()

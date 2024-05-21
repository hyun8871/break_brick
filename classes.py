import pygame
import math

class Brick:
    def __init__(self, x, y, w, h, hp, type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = hp
        self.type = type
    def display(self):
        pygame.image.load("brick.png")
    def onBallCollision(self, ball):
        if ball.
    def death(self):


class DropItem:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy 

class Ball:
    max_exp = [0]
    perks = {"dmgLv"}
    buffs = {}
    max_lv = 50
    choice = 0
    def __init__(self, x, y, vx, vy, radius):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lv = 1
        self.exp = 0
        self.dmg = 1
        for i in range(1, 51):
            self.max_exp.append(math.floor(10+2**(i/2)))
    def display(self):
        pygame.image.load("ball.png")
    def freeMove(self):
        self.x+=self.vx
        self.y+=self.vy
    def lvUpCheck(self):
        while self.exp >= self.max_exp[self.lv]:
            self.exp -= self.max_exp[self.lv]
            self.lv += 1
            self.choice += 1
    def perkSelection(self):
    def dmgCalc(self):

    def onBarCollision(self):
        
    def update(self): #매 프레임마다 업데이트 되는 공기중에서의 움직임
        self.freeMove() 
        self.lvUpCheck()
        
class Bar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def move(self): #키 입력에 따라서 Bar 좌우로 위치 이동
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            y+=1 # 속도 바꾸기
        if keys[pygame.K_RIGHT]:
            y-=1
            
def gamestart():
    pass
def gameover(score):
    pass
        
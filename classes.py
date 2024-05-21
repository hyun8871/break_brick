import pygame

class brick:
    def __init__(self, x, y, w, h, hp, type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = hp
        self.type = type
    def display(self):
        pygame.image.load("brick.png")
    def onBallCollision(self):
        
class ball:
    def __init__(self):
        pass
    def display(self):
        pygame.image.load("bar.png")
    def freeMove(self): #매 프레임마다 업데이트 되는 공기중에서의 움직임
        pass
    def onCollision(self): #충돌시 반발되는 것

class bar:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def move(self): #키 입력에 따라서 Bar 위치 이동
        pass
        
import pygame
import math
import sys
import json

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
        self.radius = radius
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
        if abs(self.x-('여기 bar 윗 경계 x값 넣을 것'))<self.radius:
            self.vx = -self.vx
    
        
        
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

def show_start_screen(screen): # 아무 키나 누르면 시작
    font = pygame.font.Font(None, 70)
    text = font.render("Press Any Key to Start", True, 'WHITE')
    text_rect = text.get_rect(center=(320, 320))
    screen.fill('BLACK')
    screen.blit(text, text_rect)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False



def gameover(screen, score):
    font = pygame.font.Font(None, 50)
    text = font.render(f"Game Over. \n Your score is {score}", True, WHITE)
    text_rect = text.get_rect(center=(320, 320))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)  # 3초 대기
        
    
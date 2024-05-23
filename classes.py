import pygame
import math
import sys
import json
import random




img_path = "sources/images/"

class Brick:
    def __init__(self, x, y, w, h, hp, type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = hp
        self.type = type
    def display(self, screen):
        img = pygame.image.load(img_path+"brick.png")
        img = pygame.transform.scale(img, (self.w, self.h))
        screen.blit(img, (self.x, self.y))
    def onBallCollision(self, ball):
        if 540-ball.y-ball.radius < self.y+self.h/2: #공이 벽돌 아래쪽에 부딪힘
            self.hp=-1
            ball.vy = -ball.vy
        elif 540-ball.y+ball.radius < self.y+self.h/2: #공이 벽돌 위쪽에 부딪힘
            self.hp=-1
            ball.vy = -ball.vy
        elif ball.x+ball.radius > self.x-self.w/2: # 공이 벽돌 왼쪽에 부딪힘
            self.hp-=1
            ball.vx = -ball.vx
        elif ball.x-ball.radius > self.x+self.w/2: # 공이 벽돌 오른쪽에 부딪힘
            self.hp-=1
            ball.vx = -ball.vx
    def death(self):
        if self.hp<=0:
            pass # 죽어라


class DropItem:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy 
    


class Boundary:
    def __init__(self, w, h):# w, h 옆 두께, 위 두께(아마 비슷할듯)
        self.w = w
        self.h = h
    def collisionwithball(self, ball):
        if ball.y-ball.radius<self.h: #위에 부딪히는 경우
            ball.vy = -ball.vy
        elif ball.x-ball.radius<self.w: # 왼쪽에 부딪히는 경우
            ball.vx = -ball.vx
        elif ball.x+ball.radius>640-self.w: # 오른쪽에 부딪히는 경우
            ball.vx = -ball.vx
        
    

class Ball:
    max_exp = [0]
    perks = {}
    buffs = {}
    with open('sources/files/perks.json', 'r', encoding='utf-8') as f:
        perks_data = json.load(f)
    
    max_lv = 30
    choice = 0
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.lv = 1
        self.exp = 0
        self.dmg = 1
        self.radius = radius
        self.on_bar = True
        for i in range(1, 51):
            self.max_exp.append(math.floor(10+2**(i/2)))
    def display(self, screen):
        img = pygame.image.load(img_path+"ball.png")
        img = pygame.transform.scale(img, (self.radius*2, self.radius*2))
        screen.blit(img, (self.x, self.y))

    def freeMove(self):
        self.x+=self.vx
        self.y+=self.vy
    def lvUpCheck(self):
        while self.exp >= self.max_exp[self.lv]:
            self.exp -= self.max_exp[self.lv]
            self.lv += 1
            self.choice += 1
    def perkSelection(self):
        if self.choice >= 1:
            random_perk_choice = list(random.choices(self.perks_data, k=3))
            
    def dmgCalc(self):
        pass

    def onBarCollision(self):
        if abs(self.x-('여기 bar 윗 경계 x값 넣을 것'))<self.radius:
            self.vx = -self.vx

    def update(self, bar): #매 프레임마다 업데이트 되는 공기중에서의 움직임
        if self.on_bar:
            self.x = bar.x
            self.y = bar.y+10
        else:
            self.freeMove() 
        self.lvUpCheck()

    def release(self, bar):
        if self.on_bar:
            self.on_bar = False
            self.vy += 8
            self.vx += 2
        
class Bar:
    vx = 10
    def __init__(self, x, y, vx, l):
        self.x = x
        self.y = y
        self.vx = vx
        self.l = l
    def display(self, screen):
        img = pygame.image.load(img_path+"bar.png")
        img = pygame.transform.scale(img, (self.l, 20))
        screen.blit(img, (self.x, self.y))
    def move(self, event): #키 입력에 따라서 Bar 좌우로 위치 이동
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_RIGHT:
                vx+=self.vx
            elif key == pygame.K_LEFT:
                vx-=self.vx
            
def gamestart(screen): # 아무 키나 누르면 시작
    font = pygame.font.Font(None, 70)
    text = font.render("Press Any Key to Start", True, 'WHITE')
    text_rect = text.get_rect(center=(270, 270))
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
    text_rect = text.get_rect(center=(270, 270))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)  # 3초 대기
        
    
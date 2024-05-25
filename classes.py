import pygame
import math
import sys
import json
import random


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900

LEFT_BOUNDARY = 10
RIGHT_BOUNDARY = SCREEN_WIDTH - 11
UPPER_BOUNDARY = 10
LOWER_BOUNDARY = SCREEN_HEIGHT - 11

img_path = "sources/images/"

class StageManager:
    bricks = []
    unbreakable_bricks = []
    stage = 0
    with open('sources/files/maps.json', 'r', encoding='utf-8') as f:
        map_list = json.load(f)
    
    def __init__(self):
        pass
    def new_stage(self):
        if len(self.bricks) == 0:
            self.stage += 1
            self.unbreakable_bricks = []
            map_type = random.choice(list(self.map_list.keys()))
            for brick in self.map_list[map_type]:
                sx, sy, ex, ey = 0, 0, 0, 0
                ub = brick.get("unbreakable", False)
                hp = brick.get("hp", 1)
                hp = math.floor(hp*1.5**(self.stage-1))
                if "x" in brick:
                    sx = ex = brick["x"]
                if "from_x" in brick and "to_x" in brick:
                    sx = brick["from_x"]    
                    ex = brick["to_x"]
                if "y" in brick:
                    sy = ey = brick["x"]
                if "from_y" in brick and "to_y" in brick:
                    sy = brick["from_x"]    
                    ey = brick["to_x"]    
                for y in range(sy, ey+1):
                    for x in range(sx, ex+1):
                        if ub: 
                            self.unbreakable_bricks.append(Brick(x, y, 0, 1))
                        else: 
                            self.bricks.append(Brick(x, y, hp, 0))
    def display_bricks(self, screen):
        for brick in self.bricks:
            brick.display(screen)
class Brick:
    w = 75
    h = 40
    def __init__(self, xi, yi, hp, type):
        self.xi = xi
        self.yi = yi
        self.hp = hp
        self.type = type
        self.img = pygame.image.load(img_path+"brick.png").convert_alpha()
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.w, self.h))
        img_rect = self.img.get_rect()
        img_rect.center = (self.xi*self.w+self.w/2, self.yi*self.h+self.h/2)
        screen.blit(self.img, img_rect)
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
        self.img = pygame.image.load(img_path+"ball.png").convert_alpha()
        
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.radius*2, self.radius*2))
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img, img_rect)

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

    def onBarCollision(self, bar):
        if abs(bar.y - self.y) <= bar.h/2:
            tmp_v = math.sqrt(self.vy**2 + self.vx**2)
            if self.x-bar.x == 0:
                tmp_deg = math.pi/2
            else:
                tmp_deg = math.atan((self.y-bar.y)/(self.x-bar.x))
            print(tmp_deg)
            self.vx = tmp_v*math.cos(tmp_deg)
            self.vy = -tmp_v*math.sin(tmp_deg)
            self.y += self.vy
    
    def onWallCollision(self):
        if self.y - UPPER_BOUNDARY < self.radius or LOWER_BOUNDARY - self.y < self.radius:
            self.vy *= -1
        if self.x - LEFT_BOUNDARY < self.radius or RIGHT_BOUNDARY - self.x < self.radius:
            self.vx *= -1

    def update(self, bar): #매 프레임마다 업데이트 되는 공기중에서의 움직임
        if self.on_bar:
            self.x = bar.x
            self.y = bar.y-20
        else:
            self.onWallCollision()
            self.onBarCollision(bar)
            self.freeMove() 
        self.lvUpCheck()

    def release(self, bar):
        if self.on_bar:
            self.on_bar = False
            self.vy = -8
            self.vx = 2
        
class Bar:
    temp_x_move = 0
    def __init__(self, x, y, vx, l):
        self.x = x
        self.y = y
        self.vx = vx
        self.l = l
        self.h = 20
        self.img = pygame.image.load(img_path+"bar.png").convert_alpha()
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.l, self.h))
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img, img_rect)
    def getmove(self, event): #키 입력에 따라서 Bar 좌우로 위치 이동
        if event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_RIGHT:
                self.temp_x_move=1
            elif key == pygame.K_LEFT:
                self.temp_x_move=-1
        if event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_RIGHT and self.temp_x_move==1:
                self.temp_x_move=0
            elif key == pygame.K_LEFT and self.temp_x_move==-1:
                self.temp_x_move=0
    def move(self):
        if self.temp_x_move == 1:
            self.x += self.vx
        elif self.temp_x_move == -1:
            self.x -= self.vx
            
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
        
    
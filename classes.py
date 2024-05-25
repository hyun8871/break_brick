import pygame
import math
import sys
import json
import random
import time
#ㅇㅇㅇㅇㅇㅇㅇ
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

LEFT_BOUNDARY = 10
RIGHT_BOUNDARY = SCREEN_WIDTH - 11
UPPER_BOUNDARY = 10
LOWER_BOUNDARY = SCREEN_HEIGHT + 10

img_path = "sources/images/"
fonts_path = "sources/fonts/"

class StageManager:
    bricks = []
    unbreakable_bricks = []
    stage = 0
    
    
    def __init__(self):
        with open('sources/files/maps.json', 'r', encoding='utf-8') as f:
            self.map_list = json.load(f)
    def new_stage(self, player):
        if len(self.bricks) == 0:
            self.stage += 1
            player.newStage()
            self.unbreakable_bricks = []
            map_type = random.choice(list(self.map_list.keys()))
            for brick in self.map_list[map_type]:
                sx, sy, ex, ey = 0, 0, 0, 0
                ub = brick.get("unbreakable", 0)
                hp = brick.get("hp", 1)
                hp = math.floor(hp*(self.stage-1+(1.6)**(self.stage-1+random.random()/3)))
                if "x" in brick:
                    sx = brick["x"]
                    ex = brick["x"]
                if "from_x" in brick and "to_x" in brick:
                    sx = brick["from_x"]    
                    ex = brick["to_x"]
                if "y" in brick:
                    sy = brick["y"]
                    ey = brick["y"]
                if "from_y" in brick and "to_y" in brick:
                    sy = brick["from_y"]    
                    ey = brick["to_y"]    
                for y in range(sy, ey+1):
                    for x in range(sx, ex+1):
                        if ub: 
                            self.unbreakable_bricks.append(UnbreakableBrick(x, y, 0))
                        else: 
                            self.bricks.append(Brick(x, y, hp))
    def bricksCollision(self, ball):
        for brick in self.bricks:
            brick.onBallCollision(ball)
        for brick in self.unbreakable_bricks:
            brick.onBallCollision(ball)
    def bricksDisplay(self, screen):
        for brick in self.bricks:
            brick.display(screen)
        for brick in self.unbreakable_bricks:
            brick.display(screen)
    def bricksDeathCheck(self, exp_manager):
        for brick in self.bricks:
            if brick.hp <= 0:
                exp_total_val = math.floor(math.sqrt(brick.max_hp)*(1+random.random()))
                while exp_total_val > 0:
                    cur_val = random.randint(math.ceil(exp_total_val/8), exp_total_val)
                    exp_total_val -= cur_val
                    exp_manager.newRandomExp(brick.x, brick.y, cur_val)
                    
                self.bricks.remove(brick)

class Brick:
    w = 75
    h = 40
    img = 0
    font = 0
    def __init__(self, xi, yi, hp):
        self.xi = xi
        self.yi = yi
        self.x = xi*self.w
        self.y = yi*self.h
        self.max_hp = hp
        self.hp = hp
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.w, self.h))
        screen.blit(self.img, (self.x, self.y))
        txt = self.font.render(str(self.hp), True, "white")
        txt_rect = txt.get_rect()
        txt_rect.center = (self.x+self.w/2, self.y+self.h/2)
        screen.blit(txt, txt_rect)
    def onBallCollision(self, ball):
        if abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius:
            if abs(self.y+self.h/2-ball.y) >= self.h/2-ball.radius:
                self.hp-=1
                ball.vy = -ball.vy
                ball.y += ball.vy
                print(self.hp)
            else:
                self.hp-=1
                ball.vx = -ball.vx
                ball.x += ball.vx
                print(self.hp)

class UnbreakableBrick(Brick):
    img = 0
    def __init__(self, xi, yi, hp):
        super().__init__(xi, yi, hp)
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.w, self.h))
        screen.blit(self.img, (self.x, self.y))
    def onBallCollision(self, ball):
        if abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius:
            if abs(self.y+self.h/2-ball.y) >= self.h/2-ball.radius:
                ball.vy = -ball.vy
                ball.y += ball.vy
                print(self.hp)
            else:
                ball.vx = -ball.vx
                ball.x += ball.vx
                print(self.hp)


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
        
    
class Player:
    max_exp = [0]
    perks = {}
    buffs = {}
    balls = []
    with open('sources/files/perks.json', 'r', encoding='utf-8') as f:
        perks_data = json.load(f)
    
    max_lv = 30
    choice = 0
    def __init__(self):
        self.lv = 1
        self.exp = 0
        self.dmg = 1
        self.ball_v = 8
        for i in range(1, 51):
            self.max_exp.append(math.floor(10+2**(i/2)))
        self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, True))
    def newStage(self):
        self.balls = []
        self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, True))
    def ballsUpdate(self, bar, stage_manager):
        for ball in self.balls:
            ball.update(bar)
            stage_manager.bricksCollision(ball)
    def ballsRelease(self, bar):
        for ball in self.balls:
            ball.release(bar)
    def ballsDisplay(self, screen):
        for ball in self.balls:
            ball.display(screen)
    def lvUpCheck(self):
        while self.exp >= self.max_exp[self.lv]:
            self.exp -= self.max_exp[self.lv]
            self.lv += 1
            self.choice += 1

    def perkSelection(self):
        if self.choice >= 1:
            random_perk_choice = list(random.choices(self.perks_data, k=3))

class ExpManager:
    exps = []
    def __init__(self):
        pass
    def newRandomExp(self, x, y, val):
        degree = 3/2*math.pi + (random.random()*2+1)*(1/15)*math.pi
        self.exps.append(Exp(x, y, 4*math.cos(degree), 4*math.sin(degree), val))
    def expsUpdate(self, bar, player):
        for exp in self.exps:
            exp.freeMove()
            if exp.isBarCollision(bar):
                player.exp += exp.val
                self.exps.remove(exp)
                continue
            if exp.low_bound == 0:
                self.exps.remove(exp)
                continue

    def expsDisplay(self, screen):
        for exp in self.exps:
            exp.display(screen)

class Exp:
    img = 0
    def __init__(self, x, y, vx, vy, val):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.val = val
        self.radius = 8*math.sqrt(val)
        self.low_bound = 3
    def onWallCollision(self):
        if self.y - UPPER_BOUNDARY < self.radius:
            self.vy *= -1
            self.y += 1.5*self.vy
        if LOWER_BOUNDARY - self.y < self.radius:
            self.vy *= -0.8
            self.y += 1.5*self.vy
            self.low_bound -= 1
        if self.x - LEFT_BOUNDARY < self.radius or RIGHT_BOUNDARY - self.x < self.radius:
            self.vx *= -1
            self.x += 1.5*self.vx
    def freeMove(self):
        self.onWallCollision()
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.radius*2, self.radius*2))
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img, img_rect)
    def isBarCollision(self, bar):
        return abs(self.y-bar.y) <= self.radius+bar.h/2 and abs(self.x-bar.x) <= self.radius+bar.l/2



class Ball:
    img = 0
    def __init__(self, x, y, radius, v, on_bar):
        self.x = x
        self.y = y
        self.v = v
        self.vx = 0
        self.vy = 0
        self.radius = radius
        self.on_bar = on_bar
        
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.radius*2, self.radius*2))
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img, img_rect)

    def freeMove(self):
        self.x+=self.vx
        self.y+=self.vy      

    def onBarCollision(self, bar):
        if abs(self.y-bar.y) <= self.radius+bar.h/2 and abs(self.x-bar.x) <= self.radius+bar.l/2:
            tmp_v = math.sqrt(self.vy**2 + self.vx**2)
            stand_dis = 2*(self.x - bar.x)/bar.l
            degree = 3/2*math.pi + (1/3)*math.pi*stand_dis
            
            self.vx = tmp_v*math.cos(degree)
            self.vy = tmp_v*math.sin(degree)
            self.x += self.vx
            self.y += self.vy
    
    def onWallCollision(self):
        if self.y - UPPER_BOUNDARY < self.radius or LOWER_BOUNDARY - self.y < self.radius:
            self.vy *= -1
            self.y += 1.5*self.vy
        if self.x - LEFT_BOUNDARY < self.radius or RIGHT_BOUNDARY - self.x < self.radius:
            self.vx *= -1
            self.x += 1.5*self.vx

    def update(self, bar): #매 프레임마다 업데이트 되는 공기중에서의 움직임
        if self.on_bar:
            self.x = bar.x
            self.y = bar.y-20
        else:
            self.onWallCollision()
            self.onBarCollision(bar)
            self.freeMove() 

    def release(self, bar):
        if self.on_bar:
            self.on_bar = False
            degree = 3/2*math.pi + (random.random()*2+1)*(1/12)*math.pi
            self.vy = self.v * math.sin(degree)
            self.vx = self.v * math.cos(degree)
        
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
        if self.temp_x_move == 1 and self.l/2<self.x + self.vx<SCREEN_WIDTH-self.l/2:
            self.x += self.vx
        elif self.temp_x_move == -1 and self.l/2<self.x - self.vx<SCREEN_WIDTH-self.l/2:
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
        
    
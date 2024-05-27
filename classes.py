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
UPPER_BOUNDARY = 120
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
            player.newStage(self.stage)
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
    def bricksCollision(self, ball, player):
        damage = player.damageCalc()
        for brick in self.bricks:
            if brick.isBallCollision(ball):
                burst = int(player.perks_data["burst"]["val1"][player.perks.get("burst", 0)])/100
                burst_damage = int(damage*burst)
                if burst_damage > 0:
                    for brick2 in self.bricks:
                        brick2.onBallRadiusCollision(ball, burst_damage, 50)
            brick.onBallCollision(ball, damage)
        for brick in self.unbreakable_bricks:
            if brick.isBallCollision(ball):
                burst = int(player.perks_data["burst"]["val1"][player.perks.get("burst", 0)])/100
                burst_damage = int(damage*burst)
                if burst_damage > 0:
                    for brick2 in self.bricks:
                        brick2.onBallRadiusCollision(ball, burst_damage, 50)
            brick.onBallCollision(ball)
    def bricksDisplay(self, screen):
        for brick in self.bricks:
            brick.display(screen)
        for brick in self.unbreakable_bricks:
            brick.display(screen)
    def bricksDeathCheck(self, drop_manager, player):
        for brick in self.bricks:
            if brick.hp <= 0:
                expPerc = int(player.perks_data["expPerc"]["val1"][player.perks.get("expPerc", 0)])/100
                exp_total_val = math.floor(math.sqrt(brick.max_hp)*(1+random.random())*(1+expPerc))
                while exp_total_val > 0:
                    cur_val = random.randint(math.ceil(exp_total_val/8), exp_total_val)
                    exp_total_val -= cur_val
                    drop_manager.newRandomExp(brick.x, brick.y, cur_val)
                itemPerc = int(player.perks_data["itemPerc"]["val1"][player.perks.get("itemPerc", 0)])/100
                if random.random() <= 0.1+itemPerc:
                    drop_manager.newRandomItem(brick.x, brick.y)
                player.score += brick.max_hp*100
                player.alarm_text.newText("+"+str(brick.max_hp*100), (184, 134, 11), 20, 1000)
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
        self.y = yi*self.h+UPPER_BOUNDARY
        self.max_hp = hp
        self.hp = hp
    def display(self, screen):
        screen.blit(self.img, (self.x, self.y))
        txt = self.font.render(str(self.hp), True, "white")
        txt_rect = txt.get_rect()
        txt_rect.center = (self.x+self.w/2, self.y+self.h/2)
        screen.blit(txt, txt_rect)
    def isBallCollision(self, ball):
        return abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius
    def onBallCollision(self, ball, dmg):
        if abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius:
            if abs(self.y+self.h/2-ball.y) >= self.h/2-ball.radius:
                self.hp-=dmg
                ball.vy = -ball.vy
                ball.y += ball.vy
            else:
                self.hp-=dmg
                ball.vx = -ball.vx
                ball.x += ball.vx
    def onBallRadiusCollision(self, ball, dmg, rad):
        if abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius+rad and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius+rad:
            self.hp-=dmg

class UnbreakableBrick(Brick):
    img = 0
    def __init__(self, xi, yi, hp):
        super().__init__(xi, yi, hp)
    def display(self, screen):
        #self.img = pygame.transform.scale(self.img, (self.w, self.h))
        screen.blit(self.img, (self.x, self.y))
    def onBallCollision(self, ball):
        if abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius:
            if abs(self.y+self.h/2-ball.y) >= self.h/2-ball.radius:
                ball.vy = -ball.vy
                ball.y += 2.5*ball.vy
            else:
                ball.vx = -ball.vx
                ball.x += 2.5*ball.vx

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

class AlarmTextManager:
    texts = []
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def newText(self, text, color, size, dur,):
        self.texts.insert(0, [text, color, size, dur, dur])
    def textDisplay(self, screen):
        cur_y = self.y
        mult = 1
        for txt, color, size, dur, max_dur in self.texts:
            left_ratio = min(1, dur*1.5/max_dur)
            color = tuple( map(lambda x: int(x*(left_ratio)+255*(1-left_ratio)), color) )
            txt_font = pygame.font.Font( fonts_path+"neodgm.ttf", math.floor(size*mult))
            txt = txt_font.render(txt, True, color)
            txt_rect = txt.get_rect()
            txt_rect.center = (self.x, cur_y)
            screen.blit(txt, txt_rect)
            cur_y -= 1.2*size*mult
            mult *= 0.7
    def textTimeTick(self):
        tick = 1000/60
        for t in self.texts:
            t[3] -= tick
            if t[3] <= 0:
                self.texts.remove(t)
    

    
class Player:
    score = 0
    p_stage = 0
    hp = 0
    max_hp = 100
    font = 0
    max_exp = [0]
    perks = {}
    buffs = {}
    balls = []
    random_perk_choice = []
    perk_selection = 0
    gui_img = 0
    roman = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    alarm_text = AlarmTextManager(SCREEN_WIDTH/2, SCREEN_HEIGHT-200)
    with open('sources/files/perks.json', 'r', encoding='utf-8') as f:
        perks_data = json.load(f)
    available_perks = list(perks_data.keys())
    for perk in perks_data.keys():
        values = [0]
        values.extend(list(perks_data[perk]["val1"].split("/")))
        perks_data[perk]["val1"] = values
    
    max_lv = 30
    choice = 0
    def __init__(self):
        self.lv = 1
        self.exp = 0
        self.dmg = 1
        self.ball_v = 8
        self.hp = 100
        self.max_hp = 100
        for i in range(1, 51):
            self.max_exp.append(math.floor(10+1.2**i*2.5))
        print(self.max_exp)
        self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, 0, True))
    def newStage(self, stage):
        self.balls = []
        self.p_stage = stage
        startBall = int(self.perks_data["startBall"]["val1"][self.perks.get("startBall", 0)])
        self.score += (stage-1)*1000
        if stage != 1: self.alarm_text.newText("Stage Clear! +"+str(stage*1000), (184, 134, 11), 30, 2000)
        for _ in range(1+startBall):
            self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, 0, True))
    def ballsUpdate(self, bar, stage_manager):
        for ball in self.balls:
            ball.update(bar)
            if ball.isBarCollision(bar):
                moreBall = int(self.perks_data["moreBall"]["val1"][self.perks.get("moreBall", 0)])
                moreBall /= 100
                degree = 3/2*math.pi + (random.random()*2-1)*(1/6)*math.pi
                if random.random() <= moreBall:
                    self.balls.append(Ball(bar.x, bar.y-10, 8, self.ball_v, degree, False))
            stage_manager.bricksCollision(ball, self)
    def ballsRelease(self, bar):
        for ball in self.balls:
            ball.release(bar)
    def ballsDeathCheck(self):
        for ball in self.balls:
            if ball.isLowerCollision():
                revive = int(self.perks_data["revive"]["val1"][self.perks.get("revive", 0)])
                revive /= 100
                rnd = random.random()
                if rnd <= revive:
                    ball.vy *= -1
                    ball.y += ball.vy
                else:
                    self.balls.remove(ball)
            if len(self.balls) == 0:
                self.hp -= self.max_hp*0.25
                startBall = int(self.perks_data["startBall"]["val1"][self.perks.get("startBall", 0)])
                self.alarm_text.newText("모든 공을 잃었습니다... hp -"+str(int(self.max_hp*0.25)), (150, 0, 0), 25, 2000)
                for _ in range(1+startBall):
                    self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, 0, True))
                
    def ballsDisplay(self, screen):
        for ball in self.balls:
            ball.display(screen)
    def lvUpCheck(self):
        while self.exp >= self.max_exp[self.lv]:
            self.exp -= self.max_exp[self.lv]
            self.lv += 1
            self.choice += 1
    def newPerkSelection(self):
        if self.choice >= 1 and len(self.random_perk_choice) == 0:
            self.random_perk_choice = list(random.sample(self.available_perks, k=3))
    def perkSelection(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.perk_selection = (self.perk_selection+1)%3
            if event.key == pygame.K_LEFT:
                self.perk_selection = (self.perk_selection-1)%3
            if event.key == pygame.K_SPACE:
                self.choice -= 1
                if self.random_perk_choice[self.perk_selection] in self.perks:
                    self.perks[self.random_perk_choice[self.perk_selection]] += 1
                    for ap in self.available_perks:
                        if self.perks.get(ap, 0) >= self.perks_data[ap].get("maxlv", 999):
                            self.available_perks.remove(ap)
                else:
                    self.perks[self.random_perk_choice[self.perk_selection]] = 1
                self.random_perk_choice = []
    def neodgm(self, text, tx, ty, size, color, screen):
        txts = text.split("$n")
        i = 0
        for txt in txts:
            txt_font = pygame.font.Font( fonts_path+"neodgm.ttf", size)
            txt = txt_font.render(txt, True, color)
            txt_rect = txt.get_rect()
            txt_rect.center = (tx, ty+size*1.2*i)
            screen.blit(txt, txt_rect)
            i+=1
    def perkDesc(self, perk, lv):
        return self.perks_data[perk]["desc"].replace("{val1}", self.perks_data[perk]["val1"][lv])
    def perkSelectionDisplay(self, screen):
    
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(200)
        s.fill((0,0,0))
        screen.blit(s, (0,0))
        self.neodgm("LEVEL UP!", SCREEN_WIDTH/2, 80, 50, "white", screen)
        self.neodgm("새 특성을 선택하세요", SCREEN_WIDTH/2, 125, 30, "white", screen)
        x_coord = [SCREEN_WIDTH/2-180, SCREEN_WIDTH/2, SCREEN_WIDTH/2+180]

        for i in range(3):
            if self.perk_selection == i: 
                pygame.draw.rect(screen, "white", [x_coord[i]-60, SCREEN_HEIGHT/2-100, 120, 120], 2)
            cur_lv = self.perks.get(self.random_perk_choice[i], 0)+1
            self.neodgm(self.perks_data[self.random_perk_choice[i]]["name"]+" "+self.roman[cur_lv], x_coord[i], SCREEN_HEIGHT/2-120, 18, "white", screen)
            self.neodgm(self.perkDesc(self.random_perk_choice[i], cur_lv), x_coord[i], SCREEN_HEIGHT/2+50, 15, "white", screen )
        self.neodgm('좌우 방향키로 특성 선택$n스페이스바로 특성 확정', SCREEN_WIDTH/2, SCREEN_HEIGHT-180, 20, "white", screen)
    def GUIDisplay(self, screen):
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, SCREEN_WIDTH, 120))
        self.neodgm("STAGE "+str(self.p_stage), SCREEN_WIDTH/2, 24, 24, "white", screen)
        self.neodgm("LV : "+str(self.lv), SCREEN_WIDTH/2, 50, 14, "white", screen)
        self.neodgm("EXP : "+str(self.exp)+" / "+str(self.max_exp[self.lv]), SCREEN_WIDTH/2, 68, 14, "white", screen)
        self.neodgm("SCORE : "+str(self.score), SCREEN_WIDTH/2, 86, 14, "white", screen)
        self.neodgm("HP : "+str(int(self.hp))+" / "+str(int(self.max_hp)), SCREEN_WIDTH/2, 104, 14, "white", screen)

    def damageCalc(self):
        dmgAdd = int(self.perks_data["dmgAdd"]["val1"][self.perks.get("dmgAdd", 0)])
        dmgMult = int(self.perks_data["dmgMult"]["val1"][self.perks.get("dmgMult", 0)])
        return math.floor(float(dmgAdd+1)*float(100+dmgMult)/100)
    def barLength(self, bar):
        barSize = int(self.perks_data["barSize"]["val1"][self.perks.get("barSize", 0)])
        bar.l = 120*(100+barSize)/100
    def onCollisionItem(self, typ):
        if typ == "bomb":
            self.hp -= 15
            self.alarm_text.newText("폭탄을 먹었습니다 hp -15", (150, 0, 0), 25, 2500)
        if typ == "damage_mult":
            self.buffs["damage_mult"] = 5000
            self.alarm_text.newText("아이템 획득! 5초간 공격력 2배", (0, 0, 0), 25, 2500)
        if typ == "bar_up":
            self.buffs["bar_up"] = 8000
            self.alarm_text.newText("아이템 획득! 8초간 바 길이 2배", (0, 0, 0), 25, 2500)
        if typ == "speed_up":
            self.buffs["speed_up"] = 5000
            self.alarm_text.newText("아이템 획득! 5초간 속도 1.5배", (0, 0, 0), 25, 2500)
        if typ == "ball_mult":
            num = len(self.balls)
            for i in range(num):
                self.balls.append(Ball(self.balls[i].x, self.balls[i].y, 8, self.ball_v, random.random()*math.pi, False))
            self.alarm_text.newText("아이템 획득! 공 갯수 두배", (0, 0, 0), 25, 2500)
    


                

class DropManager:
    drops = []
    typs = ["bomb", "ball_mult", "bar_up", "damage_mult", "speed_up"]
    def __init__(self):
        pass
    def newRandomExp(self, x, y, val):
        degree = 3/2*math.pi + (random.random()*2-1)*(1/12)*math.pi
        self.drops.append(Exp(x, y, 4*math.cos(degree), 4*math.sin(degree), val, 3))
    def newRandomItem(self, x, y):
        rnd_typ = random.choice(self.typs)
        degree = 3/2*math.pi + (random.random()*2-1)*(1/12)*math.pi
        self.drops.append(Item(x, y, 4*math.cos(degree), 4*math.sin(degree), 20, 1, rnd_typ))
    def expsUpdate(self, bar, player):
        for drop in self.drops:
            drop.freeMove()
            if drop.isBarCollision(bar):
                if isinstance(drop, Exp):
                    player.exp += drop.val
                if isinstance(drop, Item):
                    player.onCollisionItem(drop.typ)
                self.drops.remove(drop)
                continue
            if drop.low_bound == 0:
                self.drops.remove(drop)
                continue

    def expsDisplay(self, screen):
        for exp in self.drops:
            exp.display(screen)

class DropItem:
    img = 0
    def __init__(self, x, y, vx, vy, size, lb):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = size
        self.low_bound = lb
    def freeMove(self):
        self.onWallCollision()
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
    def onWallCollision(self):
        if LOWER_BOUNDARY - self.y < self.radius:
            self.vy *= -0.8
            self.y += 1.5*self.vy
            self.low_bound -= 1
        if self.x - LEFT_BOUNDARY < self.radius or RIGHT_BOUNDARY - self.x < self.radius:
            self.vx *= -1
            self.x += 1.5*self.vx
    def isBarCollision(self, bar):
        return abs(self.y-bar.y) <= self.radius+bar.h/2 and abs(self.x-bar.x) <= self.radius+bar.l/2
    def display(self, screen):
        pass

class Exp(DropItem):
    img = 0
    def __init__(self, x, y, vx, vy, val, lb):
        super().__init__(x, y, vx, vy, 8*(val)**(1/3), lb)
        self.val = val
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.radius*2, self.radius*2))
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img, img_rect)

class Item(DropItem):
    img = {}
    typs = ["bomb", "ball_mult", "bar_up", "damage_mult", "speed_up"]
    def __init__(self, x, y, vx, vy, size, lb, typ):
        super().__init__(x, y, vx, vy, size, lb)
        self.typ = typ
    def img_manage():
        for typ in Item.typs:
            Item.img[typ] = pygame.transform.scale(Item.img[typ], (40, 40))
    def display(self, screen):
        img_rect = self.img[self.typ].get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img[self.typ], img_rect)



class Ball:
    img = 0
    def __init__(self, x, y, radius, v, degree, on_bar):
        self.x = x
        self.y = y
        self.v = v
        self.vx = v*math.cos(degree)
        self.vy = v*math.sin(degree)
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
    def isBarCollision(self, bar):
        return abs(self.y-bar.y) <= self.radius+bar.h/2 and abs(self.x-bar.x) <= self.radius+bar.l/2
    def onBarCollision(self, bar):
        if self.isBarCollision(bar):
            tmp_v = math.sqrt(self.vy**2 + self.vx**2)
            stand_dis = 2*(self.x - bar.x)/bar.l
            degree = 3/2*math.pi + (1/3)*math.pi*stand_dis
            
            self.vx = tmp_v*math.cos(degree)
            self.vy = tmp_v*math.sin(degree)
            self.x += self.vx
            self.y += self.vy
    
    def isLowerCollision(self):
        return LOWER_BOUNDARY - self.y < self.radius
    def onWallCollision(self):
        if self.y - UPPER_BOUNDARY < self.radius:
            self.vy *= -1
            self.y += 2*self.vy
        if self.x - LEFT_BOUNDARY < self.radius or RIGHT_BOUNDARY - self.x < self.radius:
            self.vx *= -1
            self.x += 2*self.vx

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
            degree = 3/2*math.pi + (random.random()*2-1)*(1/6)*math.pi
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
        
    
import pygame
import math
import sys
import json
import random
import time

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 850

LEFT_BOUNDARY = 10
RIGHT_BOUNDARY = SCREEN_WIDTH - 11
UPPER_BOUNDARY = 170
LOWER_BOUNDARY = SCREEN_HEIGHT + 10

img_path = "./sources/images/"
fonts_path = "./sources/fonts/"

class StageManager:
    bricks = []
    unbreakable_bricks = []
    stage = 0
    def __init__(self):
        self.bricks = []
        self.unbreakable_bricks = []
        self.damage_indicators = []
        with open('./sources/files/maps.json', 'r', encoding='utf-8') as f:
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
    def isBrickCollision(self, ball):
        ball.collided = False
        for brick in self.bricks:
            if ball.vx*(self.x+self.w/2-ball.x)+ball.vy*(self.y+self.h/2-ball.y) >= 0 and abs(brick.y+brick.h/2-ball.y) <= brick.h/2+ball.radius and abs(brick.x+brick.w/2-ball.x) <= brick.w/2+ball.radius:
                ball.collided = True
        for brick in self.unbreakable_bricks:
            if ball.vx*(self.x+self.w/2-ball.x)+ball.vy*(self.y+self.h/2-ball.y) >= 0 and abs(brick.y+brick.h/2-ball.y) <= brick.h/2+ball.radius and abs(brick.x+brick.w/2-ball.x) <= brick.w/2+ball.radius:
                ball.collided = True
    def bricksDisplay(self, screen, ms):
        for brick in self.bricks:
            brick.shakeTick(ms)
            brick.display(screen)
        for brick in self.unbreakable_bricks:
            brick.shakeTick(ms)
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
                itemPerc = 0.15+int(player.perks_data["itemPerc"]["val1"][player.perks.get("itemPerc", 0)])/100
                if random.random() <= itemPerc:
                    drop_manager.newRandomItem(brick.x, brick.y)
                player.score += brick.max_hp*100
                player.alarm_text.newText("+"+str(brick.max_hp*100), (184, 134, 11), 25, 1000)
                self.bricks.remove(brick)
    
    

class Brick:
    w = 75
    h = 40
    img = 0
    font = 0
    shakeTimer = 0
    def __init__(self, xi, yi, hp):
        self.xi = xi
        self.yi = yi
        self.w = 75
        self.h = 40
        self.x = xi*self.w
        self.y = yi*self.h+UPPER_BOUNDARY
        self.max_hp = hp
        self.hp = hp
        self.shakeTimer = 0
    def display(self, screen):
        amp = 0
        amp2 = 0
        amp = (self.shakeTimer/100)*math.sin((self.shakeTimer)/20)
        amp2 = (self.shakeTimer/100)*math.cos((self.shakeTimer)/15)
        screen.blit(self.img, (amp+self.x, amp2+self.y))
        txt = self.font.render(str(self.hp), True, "white")
        txt_rect = txt.get_rect()
        txt_rect.center = (amp+self.x+self.w/2, amp2+self.y+self.h/2)
        screen.blit(txt, txt_rect)
    def isBallCollision(self, ball):
        return ball.vx*(self.x+self.w/2-ball.x)+ball.vy*(self.y+self.h/2-ball.y) >= 0 and abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius
    def onBallCollision(self, ball, dmg):
        if ball.vx*(self.x+self.w/2-ball.x)+ball.vy*(self.y+self.h/2-ball.y) >= 0 and abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius:
            col_d = math.atan2((ball.y-self.y-self.h/2), (ball.x-self.x-self.w/2))
            side_d = math.atan2(self.h, self.w)
            if ( col_d <= side_d and col_d >= -side_d ) or ( col_d >= math.pi-side_d ) or ( col_d <= -math.pi+side_d ):
                col_dis = math.dist((ball.x, ball.y), (self.x+self.w/2, self.y+self.h/2))
                if ball.collision_dis >= col_dis:
                    ball.collision_dis = col_dis
                    ball.collision_type = 1
            else:
                col_dis = math.dist((ball.x, ball.y), (self.x+self.w/2, self.y+self.h/2))
                if ball.collision_dis >= col_dis:
                    ball.collision_dis = col_dis
                    ball.collision_type = -1
            self.hp-=dmg
            self.shakeTimer = 350
    def shakeTick(self, ms):
        if self.shakeTimer > 0:
            self.shakeTimer -= ms
        elif self.shakeTimer < 0:
            self.shakeTimer = 0
    def onBallRadiusCollision(self, ball, dmg, rad):
        if abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius+rad and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius+rad:
            self.hp-=dmg
            self.shakeTimer = 150

class UnbreakableBrick(Brick):
    w = 75
    h = 40
    img = 0
    shakeTimer = 0
    def __init__(self, xi, yi, hp):
        super().__init__(xi, yi, hp)
    def display(self, screen):
        amp = 0
        amp2 = 0
        amp = (self.shakeTimer/100)*math.sin((self.shakeTimer)/20)
        amp2 = (self.shakeTimer/100)*math.cos((self.shakeTimer)/15)
        screen.blit(self.img, (amp+self.x, amp2+self.y))
    def onBallCollision(self, ball):
        if ball.vx*(self.x+self.w/2-ball.x)+ball.vy*(self.y+self.h/2-ball.y) >= 0 and abs(self.y+self.h/2-ball.y) <= self.h/2+ball.radius and abs(self.x+self.w/2-ball.x) <= self.w/2+ball.radius:
            col_d = math.atan2((ball.y-self.y-self.h/2), (ball.x-self.x-self.w/2))
            side_d = math.atan2(self.h, self.w)
            if ( col_d <= side_d and col_d >= -side_d ) or ( col_d >= math.pi-side_d ) or ( col_d <= -math.pi+side_d ):
                col_dis = math.dist((ball.x, ball.y), (self.x+self.w/2, self.y+self.h/2))
                if ball.collision_dis >= col_dis:
                    ball.collision_dis = col_dis
                    ball.collision_type = 1
            else:
                col_dis = math.dist((ball.x, ball.y), (self.x+self.w/2, self.y+self.h/2))
                if ball.collision_dis >= col_dis:
                    ball.collision_dis = col_dis
                    ball.collision_type = -1
            self.shakeTimer = 300
            

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
        self.texts = []
    def newText(self, text, color, size, dur):
        self.texts.insert(0, [text, color, size, dur, dur, self.y, size])
    def textDisplay(self, screen):
        cur_y = self.y
        mult = 1
        index = 0
        for txt, color, cur_size, dur, max_dur, bef_y, max_size in self.texts:
            left_ratio = min(1, dur*1.6/max_dur)
            color = tuple( map(lambda x: int(x*(left_ratio)+255*(1-left_ratio)), color) )
            self.texts[index][2] = min(self.texts[index][2], math.floor(max_size*mult))
            txt_font = pygame.font.Font( fonts_path+"neodgm.ttf", self.texts[index][2])
            txt = txt_font.render(txt, True, color)
            txt_rect = txt.get_rect()
            cur_y -= 1.4*self.texts[index][2]*mult
            self.texts[index][5] = min(cur_y, self.texts[index][5])
            txt_rect.center = (self.x, self.texts[index][5])
            screen.blit(txt, txt_rect)
            mult *= 0.9
            index += 1
    def textTimeTick(self, ms):
        for t in self.texts:
            t[3] -= ms
            if t[3] <= 0:
                self.texts.remove(t)
    

    
class Player:
    score = 0
    p_stage = 0
    hp = 0
    max_hp = 100
    health_timer = 2000
    font = 0
    max_exp = [0]
    perks = {}
    perk_images = {}
    buffs = {}
    balls = []
    random_perk_choice = []
    perk_selection = 0
    gui_img = 0
    roman = [0, 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    alarm_text = 0
    with open('./sources/files/perks.json', 'r', encoding='utf-8') as f:
        perks_data = json.load(f)
    available_perks = list(perks_data.keys())
    for perk in perks_data.keys():
        values = [0]
        values.extend(list(perks_data[perk]["val1"].split("/")))
        perks_data[perk]["val1"] = values
    
    max_lv = 30
    choice = 0
    def loadImages():
        for perk in Player.perks_data:
            Player.perk_images[perk] = pygame.image.load(img_path+"perk_icons/"+perk+".png").convert_alpha()
            Player.perk_images[perk] = pygame.transform.scale(Player.perk_images[perk], (100, 100))
    def __init__(self):
        self.lv = 1
        self.exp = 0
        self.dmg = 1
        self.ball_v = 6
        self.hp = 100
        self.max_hp = 100
        self.health_timer = 2000
        self.max_exp = [0]
        self.perks = {}
        self.buffs = {}
        self.balls = []
        self.p_stage = 0
        self.score = 0
        self.alarm_text = AlarmTextManager(SCREEN_WIDTH/2, SCREEN_HEIGHT-160)
        for i in range(1, 51):
            self.max_exp.append(math.floor(4+i*2+1.2**(i-1)*2.5))
        print(self.max_exp)
        self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, 0, True))
    def newStage(self, stage):
        self.balls = []
        self.p_stage = stage
        startBall = int(self.perks_data["startBall"]["val1"][self.perks.get("startBall", 0)])
        self.score += (stage-1)*1000
        self.hp = min(self.hp+30, self.max_hp)
        if stage != 1: 
            self.alarm_text.newText("Hp +30", (219, 60, 60), 30, 4000)
            self.alarm_text.newText("Stage Clear! +"+str(stage*1000), (184, 134, 11), 30, 4000)
        for _ in range(1+startBall):
            self.balls.append(Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, self.ball_v, 0, True))

    def gamestart(self, screen): # 아무 키나 누르면 시작
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
    
    def gameoverDisplay(self, screen, player):
        screen.fill('black')
        self.neodgm(f"GAME OVER", SCREEN_WIDTH/2, 270, 50, "white", screen)
        self.neodgm(f"SCORE : {player.score}", SCREEN_WIDTH/2, 350, 30, "white", screen)
        self.neodgm(f"Space Bar를 눌러 처음부터 시작합니다", SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 25, "white", screen)
        pygame.display.flip()

    def healthTimer(self, ms):
        if self.health_timer > 0:
            self.health_timer -= ms
        else:
            self.hp -= 1
            self.health_timer = max(2000-30*self.p_stage, 500)
    
    def ballsUpdate(self, bar, stage_manager):
        
        for ball in self.balls:
            ball.update(bar)
            if ball.isBarCollision(bar):
                moreBall = int(self.perks_data["moreBall"]["val1"][self.perks.get("moreBall", 0)])
                moreBall /= 100
                degree = 3/2*math.pi + (random.random()*2-1)*(1/6)*math.pi
                if random.random() <= moreBall:
                    self.balls.append(Ball(bar.x, bar.y-20, 8, self.ball_v, degree, False))
            stage_manager.bricksCollision(ball, self)
        for ball in self.balls:
            ball.collisionHandling()
        for ball in self.balls:
            stage_manager.isBrickCollision(ball)
        
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
                self.alarm_text.newText("모든 공을 잃었습니다... hp -"+str(int(self.max_hp*0.25)), (150, 0, 0), 25, 3000)
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
            img_rect = Player.perk_images[self.random_perk_choice[i]].get_rect()
            img_rect.center = (x_coord[i], SCREEN_HEIGHT/2-40)
            screen.blit(Player.perk_images[self.random_perk_choice[i]], img_rect)
            self.neodgm(self.perkDesc(self.random_perk_choice[i], cur_lv), x_coord[i], SCREEN_HEIGHT/2+50, 15, "white", screen )
        self.neodgm('좌우 방향키로 특성 선택$n스페이스바로 특성 확정', SCREEN_WIDTH/2, SCREEN_HEIGHT-180, 20, "white", screen)
    def pauseDisplay(self, screen):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(220)
        s.fill((0,0,0))
        screen.blit(s, (0,0))
        self.neodgm("- 보유 특성 -", SCREEN_WIDTH/2, 220, 30, "white", screen)
        cur_y = 260
        for perk in list(self.perks.keys()):
            self.neodgm(self.perks_data[perk]["name"]+" "+self.roman[self.perks[perk]], SCREEN_WIDTH/2, cur_y, 20, "white", screen)
            cur_y += 25
        self.neodgm("Game Paused", SCREEN_WIDTH/2, SCREEN_HEIGHT-150, 30, "white", screen)
        self.neodgm("Esc를 눌러 재시작", SCREEN_WIDTH/2, SCREEN_HEIGHT-110, 20, "white", screen)
    def GUIDisplay(self, screen):
        pygame.draw.rect(screen, (20, 20, 20), (0, 0, SCREEN_WIDTH, 60))
        pygame.draw.rect(screen, (40, 40, 40), (0, 60, SCREEN_WIDTH, 110))
        self.neodgm("STAGE "+str(self.p_stage), SCREEN_WIDTH/2, 22, 30, "white", screen)
        self.neodgm("SCORE : "+str(self.score), SCREEN_WIDTH/2, 47, 16, "white", screen)
        self.neodgm("Player Level : "+str(self.lv), SCREEN_WIDTH/2, 78, 20, "white", screen)
        self.neodgm("EXP : "+str(self.exp)+" / "+str(self.max_exp[self.lv]), SCREEN_WIDTH/2, 105, 15, "white", screen)
        exp_ratio = int((SCREEN_WIDTH-100)*(self.exp/self.max_exp[self.lv]))
        pygame.draw.line(screen, (10, 10, 10), (50, 120), (SCREEN_WIDTH-50, 120), 5)
        pygame.draw.line(screen, (249, 255, 193), (50, 120), (50+exp_ratio, 120), 5)
        self.neodgm("HP : "+str(int(self.hp))+" / "+str(int(self.max_hp)), SCREEN_WIDTH/2, 140, 15, "white", screen)
        hp_ratio = int((SCREEN_WIDTH-100)*(self.hp/self.max_hp))
        pygame.draw.line(screen, (10, 10, 10), (50, 155), (SCREEN_WIDTH-50, 155), 5)
        pygame.draw.line(screen, (255, 95, 95), (50, 155), (50+hp_ratio, 155), 5)
    def damageCalc(self):
        dmgAdd = int(self.perks_data["dmgAdd"]["val1"][self.perks.get("dmgAdd", 0)])
        dmgMult = int(self.perks_data["dmgMult"]["val1"][self.perks.get("dmgMult", 0)])
        cur_dmg = math.floor(float(dmgAdd+1)*float(100+dmgMult)/100)
        if "damage_mult" in self.buffs:
            cur_dmg *= 2
        return cur_dmg
    def onCollisionItem(self, typ):
        if typ == "bomb":
            self.hp -= 15
            self.alarm_text.newText("폭탄을 먹었습니다 hp -15", (150, 0, 0), 25, 3000)
        if typ == "damage_mult":
            self.buffs["damage_mult"] = 5000
            self.alarm_text.newText("아이템 획득! 5초간 공격력 2배", (0, 0, 0), 25, 3000)
        if typ == "bar_up":
            self.buffs["bar_up"] = 8000
            self.alarm_text.newText("아이템 획득! 8초간 바 길이 1.5배", (0, 0, 0), 25, 3000)
        if typ == "heart":
            self.hp = min(self.hp+5, self.max_hp)
            self.alarm_text.newText("하트를 먹었습니다! hp +5", (220, 60, 60), 25, 3000)
        if typ == "ball_mult":
            num = len(self.balls)
            for i in range(num):
                self.balls.append(Ball(self.balls[i].x, self.balls[i].y, 8, self.ball_v, (-1+2*random.random())*math.pi, False))
            self.alarm_text.newText("아이템 획득! 공 갯수 두배", (0, 0, 0), 25, 3000)
    def buffTimer(self, ms):
        keyss = list(self.buffs.keys())
        for buff in keyss:
            self.buffs[buff] -= ms
            if self.buffs[buff] <= 0:
                self.buffs.pop(buff)
                

    


                

class DropManager:
    drops = []
    typs = ["bomb", "ball_mult", "bar_up", "damage_mult", "heart", "heart", "heart", "heart"]
    def __init__(self):
        self.drops = []
    def newRandomExp(self, x, y, val):
        degree = 3/2*math.pi + (random.random()*2-1)*(1/12)*math.pi
        self.drops.append(Exp(x, y, 4*math.cos(degree), 4*math.sin(degree), val, 3))
    def newRandomItem(self, x, y):
        rnd_typ = random.choice(self.typs)
        degree = 3/2*math.pi + (random.random()*2-1)*(1/12)*math.pi
        if rnd_typ == "heart":
            self.drops.append(Item(x, y, 4*math.cos(degree), 4*math.sin(degree), 10, 3, rnd_typ))
        else:
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
    typs = ["bomb", "ball_mult", "bar_up", "damage_mult", "heart"]
    def __init__(self, x, y, vx, vy, size, lb, typ):
        super().__init__(x, y, vx, vy, size, lb)
        self.typ = typ
    def img_manage():
        for typ in Item.typs:
            if typ == "heart":
                Item.img[typ] = pygame.transform.scale(Item.img[typ], (20, 20))
            else:
                Item.img[typ] = pygame.transform.scale(Item.img[typ], (40, 40))
    def display(self, screen):
        img_rect = self.img[self.typ].get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img[self.typ], img_rect)



class Ball:
    img = 0
    collision_type = 0
    collision_dis = 1000
    collided = False
    def __init__(self, x, y, radius, v, degree, on_bar):
        self.x = x
        self.y = y
        self.v = v
        self.vx = v*math.cos(degree)
        self.vy = v*math.sin(degree)
        self.radius = radius
        self.on_bar = on_bar
        self.collision_dis = 1000
        self.collided = False
    def display(self, screen):
        self.img = pygame.transform.scale(self.img, (self.radius*2, self.radius*2))
        img_rect = self.img.get_rect()
        img_rect.center = (self.x, self.y)
        screen.blit(self.img, img_rect)
    def collisionHandling(self):
        if not self.collided:
            if self.collision_type == 1:
                self.vx *= -1
                self.x += 1.5*self.vx
                self.collision_type = 0
                self.collision_dis = 1000
            elif self.collision_type == -1:
                self.vy *= -1
                self.y += 1.5*self.vy
                self.collision_type = 0
                self.collision_dis = 1000
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
        if self.temp_x_move == 1 and self.x + self.vx<SCREEN_WIDTH-self.l/2:
            self.x += self.vx
        elif self.temp_x_move == -1 and self.l/2<self.x - self.vx:
            self.x -= self.vx
    def barUpdateLength(self, player):
        barSize = int(player.perks_data["barSize"]["val1"][player.perks.get("barSize", 0)])
        self.l = 120*(100+barSize)/100
        if "bar_up" in player.buffs:
            self.l *= 1.5
        

        
    
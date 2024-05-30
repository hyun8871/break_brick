import pygame
import classes
import os

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 850

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brick Break")
running = True
screen_type = "main"
perk_selecting = False
clock = pygame.time.Clock()
fonts_path = __file__+"\\..\\sources\\fonts\\"

def neodgm(text, tx, ty, size, color, screen):
    txts = text.split("$n")
    i = 0
    for txt in txts:
        txt_font = pygame.font.Font( fonts_path+"neodgm.ttf", size)
        txt = txt_font.render(txt, True, color)
        txt_rect = txt.get_rect()
        txt_rect.center = (tx, ty+size*1.2*i)
        screen.blit(txt, txt_rect)
        i+=1

def game_initiation():
    global bar, bricks, stage_manager, player, exp_manager, collision_manager
    img_path = __file__+"\\..\\sources\\images\\"
    fonts_path = __file__+"\\..\\sources\\fonts\\"
    classes.Brick.img = pygame.image.load(img_path+"brick.png").convert_alpha()
    classes.Brick.img = pygame.transform.scale(classes.Brick.img, (classes.Brick.w, classes.Brick.h))
    classes.Brick.font = pygame.font.Font( fonts_path+"neodgm.ttf", 30)
    classes.UnbreakableBrick.img = pygame.image.load(img_path+"brick_unbreakable.png").convert_alpha()
    classes.UnbreakableBrick.img = pygame.transform.scale(classes.UnbreakableBrick.img, (classes.UnbreakableBrick.w, classes.UnbreakableBrick.h))
    classes.Ball.img = pygame.image.load(img_path+"ball.png").convert_alpha()
    classes.Exp.img = pygame.image.load(img_path+"orb_exp.png").convert_alpha()
    classes.Item.img["damage_mult"] = pygame.image.load(img_path+"items\\damage_mult.png").convert_alpha()
    classes.Item.img["bar_up"] = pygame.image.load(img_path+"items\\bar_up.png").convert_alpha()
    classes.Item.img["ball_mult"] = pygame.image.load(img_path+"items\\ball_mult.png").convert_alpha()
    classes.Item.img["speed_up"] = pygame.image.load(img_path+"items\\speed_up.png").convert_alpha()
    classes.Item.img["bomb"] = pygame.image.load(img_path+"items\\bomb.png").convert_alpha()
    classes.Item.img["heart"] = pygame.image.load(img_path+"items\\heart.png").convert_alpha()
    classes.Item.img_manage()
    classes.Player.loadImages()
    bar = classes.Bar(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 10, 120)
    bricks = []
    stage_manager = classes.StageManager()
    player = classes.Player()
    exp_manager = classes.DropManager()
    collision_manager = classes.CollisionManager()

one_tick_ms = 0
start = 0
end = 0
pause = False
best_scores = []

def updateBestscore(score):
    global best_scores
    f = open(__file__+"\\..\\sources\\files\scores.txt", 'r')
    lines = f.readlines()
    f.close()
    lines = list(map(lambda x: int(x.replace("\n", "")), lines))
    if score > 0:
        lines.append(score)
    lines.sort(reverse = True)
    best_scores = lines
    f = open(__file__+"\\..\\sources\\files\scores.txt", 'w')
    txt = "\n".join(map(str, lines))
    print(txt)
    f.write(txt)
    f.close()

updateBestscore(0)

while running:
    start = pygame.time.get_ticks()
    clock.tick(60)
    if screen_type == "main":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    game_initiation()
                    screen_type = 'ingame'
        screen.fill('black')
        neodgm("Brick Break", SCREEN_WIDTH/2, 270, 50, "white", screen)
        neodgm("Best Scores", SCREEN_WIDTH/2, 400, 25, "white", screen)
        index = 1
        for scor in best_scores:
            neodgm(str(index)+". "+str(scor), SCREEN_WIDTH/2, 430+20*(index-1), 16, "white", screen)
            if index >= 10:
                break
            index+=1
        if len(best_scores) == 0:
            neodgm("...", SCREEN_WIDTH/2, 430, 16, "white", screen)
        neodgm("Space Bar를 눌러 시작합니다", SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 25, "white", screen)
        pygame.display.flip()
         
    elif screen_type == "ingame":
        #event handling
        if player.choice == 0 and not pause:
            stage_manager.new_stage(player)
            bar.barUpdateLength(player)
            exp_manager.expsUpdate(bar, player)
            player.alarm_text.textTimeTick(one_tick_ms)
            player.lvUpCheck()
            player.ballsDeathCheck()
            player.buffTimer(one_tick_ms)
            player.healthTimer(one_tick_ms)
            collision_manager.updateCollision(player.balls, stage_manager.bricks, player)
            stage_manager.bricksDeathCheck(exp_manager, player)
            player.ballsOtherCollision(bar)
            for event in pygame.event.get():
                bar.getmove(event)
                if event.type == pygame.QUIT:
                    running = False 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.ballsRelease(bar)
                    if event.key == pygame.K_ESCAPE:
                        pause = True
            bar.move()
            if player.hp<=0:
                updateBestscore(player.score)
                screen_type = 'dead'
        elif pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause = False
                    if event.key==pygame.K_SPACE:
                        game_initiation()
                        pause = False
                        screen_type = 'ingame'

        else:
            bar.temp_x_move = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                player.perkSelection(event)
                
        player.newPerkSelection()  
        
        #display
        screen.fill('white')
        stage_manager.bricksDisplay(screen, one_tick_ms)
        player.ballsDisplay(screen)
        exp_manager.expsDisplay(screen)
        player.alarm_text.textDisplay(screen) 
        bar.display(screen)
        if pause:
            player.pauseDisplay(screen)
        player.GUIDisplay(screen)
        if player.choice > 0:
            player.perkSelectionDisplay(screen)
        
        pygame.display.update()

    elif screen_type == "dead":
        player.gameoverDisplay(screen,player,best_scores)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_SPACE:
                    game_initiation()
                    screen_type = 'ingame'
    
    one_tick_ms = pygame.time.get_ticks()-start

pygame.quit()

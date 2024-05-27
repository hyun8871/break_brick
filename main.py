import pygame
import classes

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

pygame.init()




screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Collision at boundary")

clock = pygame.time.Clock()
img_path = "sources/images/"
fonts_path = "sources/fonts/"
classes.Brick.img = pygame.image.load(img_path+"brick.png").convert_alpha()
classes.Brick.img = pygame.transform.scale(classes.Brick.img, (classes.Brick.w, classes.Brick.h))
classes.Brick.font = pygame.font.Font( fonts_path+"neodgm.ttf", 30)
classes.UnbreakableBrick.img = pygame.image.load(img_path+"brick_unbreakable.png").convert_alpha()
classes.UnbreakableBrick.img = pygame.transform.scale(classes.UnbreakableBrick.img, (classes.UnbreakableBrick.w, classes.UnbreakableBrick.h))
classes.Ball.img = pygame.image.load(img_path+"ball.png").convert_alpha()
classes.Exp.img = pygame.image.load(img_path+"orb_exp.png").convert_alpha()
classes.Item.img["damage_mult"] = pygame.image.load(img_path+"items/damage_mult.png").convert_alpha()
classes.Item.img["bar_up"] = pygame.image.load(img_path+"items/bar_up.png").convert_alpha()
classes.Item.img["ball_mult"] = pygame.image.load(img_path+"items/ball_mult.png").convert_alpha()
classes.Item.img["speed_up"] = pygame.image.load(img_path+"items/speed_up.png").convert_alpha()
classes.Item.img["bomb"] = pygame.image.load(img_path+"items/bomb.png").convert_alpha()
classes.Item.img_manage()

running = True
screen_type = "main"
perk_selecting = False

bar = classes.Bar(SCREEN_WIDTH/2, SCREEN_HEIGHT-120, 8, 120)
bricks = []
stage_manager = classes.StageManager()
player = classes.Player()
exp_manager = classes.DropManager()

while running:
    clock.tick(60)

    if screen_type == "main":
        print("ds")
        screen_type = "ingame"
         
    elif screen_type == "ingame":
        #event handling
        if player.choice == 0:
            stage_manager.new_stage(player)
            player.ballsUpdate(bar, stage_manager)
            stage_manager.bricksDeathCheck(exp_manager, player)
            exp_manager.expsUpdate(bar, player)
            player.alarm_text.textTimeTick()
            player.lvUpCheck()
            for event in pygame.event.get():
                bar.getmove(event)
                if event.type == pygame.QUIT:
                    running = False 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.ballsRelease(bar)
            bar.move()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                player.perkSelection(event)
                
        player.newPerkSelection()  
        
        #display
        screen.fill('white')
        stage_manager.bricksDisplay(screen)
        player.ballsDisplay(screen)
        player.GUIDisplay(screen)
        player.barLength(bar)
        player.ballsDeathCheck()
        exp_manager.expsDisplay(screen)
        player.alarm_text.textDisplay(screen)
        bar.display(screen)
        for brick in bricks:
            brick.display(screen)
        if player.choice > 0:
            player.perkSelectionDisplay(screen)
        pygame.display.flip()
    elif screen_type == "dead":
        pass
                

pygame.quit()

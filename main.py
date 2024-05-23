import pygame
import classes

SCREEN_WIDTH = 540
SCREEN_HEIGHT = 1080

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Collision at boundary")
clock = pygame.time.Clock()

running = True
screen_type = "main"
perk_selecting = False

ball = classes.Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 0, 0, 5)
bar = classes.Bar(SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 10, 100)
bricks = []


while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
    if screen_type == "main":
        screen_type = "ingame"
    elif screen_type == "ingame":
        if not ball.perk_selecting:
            
            #display
            ball.display(screen)
            bar.display(screen)
            for brick in bricks:
                brick.display(screen)

            #event handling
            for event in pygame.event.get():
                bar.move(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ball.release(bar)
        else:
            pass
            

    
        
    pygame.display.flip()

pygame.quit()
#### dkdkdkdkdk
import pygame
import classes

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Collision at boundary")
pygame.key.set_repeat (1,1)
clock = pygame.time.Clock()

running = True
screen_type = "main"
perk_selecting = False

ball = classes.Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 5)
bar = classes.Bar(SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 10, 100)
bricks = []


while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
    if screen_type == "main":
        print("ds")
        screen_type = "ingame"
    elif screen_type == "ingame":
        if ball.choice == 0:
            
            ball.update(bar)

            #display
            screen.fill('white')
            ball.display(screen)
            bar.display(screen)
            for brick in bricks:
                brick.display(screen)
            pygame.display.flip()

            #event handling

            bar.move()
            for event in pygame.event.get():
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ball.release(bar)
        else:
            pass

pygame.quit()
#### dkdkdkdkdk
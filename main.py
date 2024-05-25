import pygame
import classes

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Collision at boundary")
clock = pygame.time.Clock()

running = True
screen_type = "main"
perk_selecting = False

ball = classes.Ball(SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 5)
bar = classes.Bar(SCREEN_WIDTH/2, SCREEN_HEIGHT-100, 10, 100)
bricks = []


# 현석아 이거 보임??
while running:
    clock.tick(60)

    if screen_type == "main":
        print("ds")
        screen_type = "ingame"
        
    elif screen_type == "ingame":
        if ball.choice == 0:
            
            ball.update(bar)

            for event in pygame.event.get():
                bar.getmove(event)
                if event.type == pygame.QUIT:
                    running = False 
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        ball.release(bar)
            bar.move()

            #display
            screen.fill('white')
            ball.display(screen)
            bar.display(screen)
            for brick in bricks:
                brick.display(screen)
            pygame.display.flip()
                
        else:
            pass

pygame.quit()

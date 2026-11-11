import pygame
from sys import exit

#initializes pygame
pygame.init()
#sets the screen dimensions
screen = pygame.display.set_mode((2560, 1664))
#creates a clock function to set FPS
clock = pygame.time.Clock()
#creates a name for the game
pygame.display.set_caption('Test game!')

test_surface = pygame.Surface((800, 400))
test_surface.fill('Red')

while True:
    for event in pygame.event.get():
        #if the user clicks the x, quits the program
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(test_surface, (200, 100))

    #updates the display
    pygame.display.update()
    #limits the while loop to 60 FPS
    clock.tick(60)
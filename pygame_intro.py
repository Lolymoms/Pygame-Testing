#most of the code is from the youtube video https://www.youtube.com/watch?v=AY9MnQ4x3zk !!
#sprites by me

import pygame
from sys import exit

#initializes pygame
pygame.init()
#sets the screen dimensions
screen = pygame.display.set_mode((1280, 832))
#creates a clock function to set FPS
clock = pygame.time.Clock()
#creates a name for the game
pygame.display.set_caption('Test game!')
#creates a font
test_font = pygame.font.Font(None, 20)

#creates a surface with a character guy
character_surface_base = pygame.image.load('Images/character.png').convert_alpha()
#makes the character bigger
character_surface = pygame.transform.scale_by(character_surface_base, 5)
#makes and grows the enemy
enemy_surface_base = pygame.image.load('Images/enemy.png').convert_alpha()
enemy_surface = pygame.transform.scale_by(enemy_surface_base, 5)
#makes the ground and background
sky_surface_base = pygame.image.load('Images/sky.png').convert()
ground_surface_base = pygame.image.load('Images/ground.png').convert()
sky_surface = pygame.transform.scale_by(sky_surface_base, 15)
sky_surface_2 = sky_surface.copy()
ground_surface = pygame.transform.scale_by(ground_surface_base, 10)
#creates a surface with text
text_surface = test_font.render('My Game', False, 'Blue')
text_rectangle = text_surface.get_rect(center = (640, 200))

character_rectangle = character_surface.get_rect(midbottom = (170, 700))
enemy_rectangle = enemy_surface.get_rect(bottomright = (1500, 700))

enemy_x_pos = 1500
sky_x_pos = 0
sky_2_x_pos = 2250
ground_x_pos_list = [0, 300, 600, 900, 1200, 1500]

while True:
    for event in pygame.event.get():
        #if the user clicks the x, quits the program
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    #moves the enemy
    enemy_rectangle.left -= 5
    if enemy_rectangle.left < -150: enemy_rectangle.left = 1500

    #makes and moves the sky and ground
    screen.blit(sky_surface, (sky_x_pos, 0))
    screen.blit(sky_surface_2, (sky_2_x_pos, 0))
    sky_x_pos -= 2
    sky_2_x_pos -= 2
    if sky_x_pos < -2300:
        sky_x_pos = 2250
    elif sky_2_x_pos < -2300:
        sky_2_x_pos = 2250

    for number in range(len(ground_x_pos_list)):
        ground_x_pos_list[number] -= 5
        if ground_x_pos_list[number] < -300:
            ground_x_pos_list[number] = 1500
    for x_pos in ground_x_pos_list:
        screen.blit(ground_surface, (x_pos, 700))

    screen.blit(character_surface, character_rectangle)
    screen.blit(enemy_surface, enemy_rectangle)
    screen.blit(text_surface, text_rectangle)

    #updates the display
    pygame.display.update()
    #limits the while loop to 60 FPS
    clock.tick(60)
#most of the code is from the youtube video https://www.youtube.com/watch?v=AY9MnQ4x3zk !!
#sprites by me
#font from https://www.1001fonts.com/lower-pixel-font.html , so don't sell this game! Personal use only >:(

import pygame
from sys import exit
import time
import random

#starting speeds
enemy_speed = 7
background_speed = 3

#initializes pygame
pygame.init()
#sets the screen dimensions
screen = pygame.display.set_mode((1280, 832))
#creates a clock function to set FPS
clock = pygame.time.Clock()
#creates a name for the game
pygame.display.set_caption('Test game!')
#creates a font
test_font = pygame.font.Font('Fonts/pixel_font.otf', 100)

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
text_surface = test_font.render('My Game', False, 'Black')
text_rectangle = text_surface.get_rect(center = (640, 100))
#creates the rectangle behind the text
text_reading_rectangle = pygame.Rect(0, 0, 400, 90)
text_reading_rectangle.center = 645, 85

character_rectangle = character_surface.get_rect(midbottom = (170, 700))
enemy_rectangle = enemy_surface.get_rect(bottomright = (1500, 700))
enemy_hitbox_rectangle = enemy_rectangle.inflate(-80, -100)

enemy_x_pos = 1500
sky_x_pos = 0
sky_2_x_pos = 2250
ground_x_pos_list = [0, 300, 600, 900, 1200, 1500]
player_gravity = 0
score = 0
score_threshold = 5

while True:
    for event in pygame.event.get():
        #if the user clicks the x, quits the program
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and character_rectangle.bottom == 700:
                player_gravity = -20
                character_rectangle.bottom -= 1

    if score >= score_threshold:
        score_threshold += 5
        enemy_speed += 1
        background_speed += 1

    #makes and moves the sky and ground
    screen.blit(sky_surface, (sky_x_pos, 0))
    screen.blit(sky_surface_2, (sky_2_x_pos, 0))
    sky_x_pos -= background_speed
    sky_2_x_pos -= background_speed
    if sky_x_pos < -2300:
        sky_x_pos = 2250
    elif sky_2_x_pos < -2300:
        sky_2_x_pos = 2250

    for number in range(len(ground_x_pos_list)):
        ground_x_pos_list[number] -= enemy_speed
        if ground_x_pos_list[number] < -300:
            ground_x_pos_list[number] = 1500
    for x_pos in ground_x_pos_list:
        screen.blit(ground_surface, (x_pos, 700))

    #player
    if character_rectangle.bottom < 700:
        player_gravity += 0.75
        character_rectangle.y += player_gravity
    if character_rectangle.bottom > 700:
        character_rectangle.bottom = 700
    screen.blit(character_surface, character_rectangle)
    #enemy
    #moves the enemy
    enemy_rectangle.left -= enemy_speed
    if enemy_rectangle.left < -150: 
        enemy_spawn = random.randint(1300, 1700)
        enemy_rectangle.left = enemy_spawn
        score += 1
    enemy_hitbox_rectangle.center = enemy_rectangle.center
    screen.blit(enemy_surface, enemy_rectangle)
    #text
    pygame.draw.rect(screen, (25, 19, 145), text_reading_rectangle)
    text_surface = test_font.render(f'Score: {score}', False, 'Black')
    screen.blit(text_surface, text_rectangle)

    #collision
    if character_rectangle.colliderect(enemy_hitbox_rectangle):
        #death animation
        player_gravity = -20
        time.sleep(1)
        while True:
            player_gravity += 0.65
            character_rectangle.y += player_gravity
            screen.blit(sky_surface, (sky_x_pos, 0))
            screen.blit(sky_surface_2, (sky_2_x_pos, 0))
            for x_pos in ground_x_pos_list:
                screen.blit(ground_surface, (x_pos, 700))
            screen.blit(enemy_surface, enemy_rectangle)
            screen.blit(character_surface, character_rectangle)
            pygame.display.update()
            if character_rectangle.bottom >= 1200:
                exit()

    #updates the display
    pygame.display.update()
    #limits the while loop to 60 FPS
    clock.tick(60)
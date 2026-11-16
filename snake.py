#13 pixels per big pixel
#65 pixels per square
#(32, 32) middle pixel

import pygame
from sys import exit
from random import randint
from copy import deepcopy

pygame.init()
screen = pygame.display.set_mode((806, 806))
clock = pygame.time.Clock()
pygame.display.set_caption('Snake')

checkerboard = pygame.image.load('Images/snake_background.png').convert()
checkerboard = pygame.transform.scale(checkerboard, (806, 806))

original_shark = pygame.image.load('Images/shark/shark_1.png').convert_alpha()
shark = pygame.transform.scale_by(original_shark, 0.5)
shark_rectangle = shark.get_rect(center = (45, 45))
shark_start = pygame.Vector2(45, 45)
shark_target = pygame.Vector2(45, 45)
shark_tail = []

original_fish = pygame.image.load('Images/fish/fish_1.png').convert_alpha()
fish = pygame.transform.scale_by(original_fish, 0.04)
fish_rectangle = fish.get_rect(center = (45, 45))

shark_movement = pygame.event.custom_type()

game_active = True
movement = False
shark_coordinates = [1, 1]
movement_dictionary = {
    pygame.K_d : [(1, 0), 0, pygame.K_a, 'Right'],
    pygame.K_w : [(0, -1), 90, pygame.K_s, 'Up'],
    pygame.K_a : [(-1, 0), 180, pygame.K_d, 'Left'],
    pygame.K_s : [(0, 1), 270, pygame.K_w, 'Down']
}
animation_frames = {
    1 : pygame.image.load('Images/shark/shark_1.png').convert_alpha(),
    2 : pygame.image.load('Images/shark/shark_2.png').convert_alpha(),
    3 : pygame.image.load('Images/shark/shark_3.png').convert_alpha(),
    4 : pygame.image.load('Images/shark/shark_3.png').convert_alpha(),
    5 : pygame.image.load('Images/shark/shark_2.png').convert_alpha(),
    6 : pygame.image.load('Images/shark/shark_1.png').convert_alpha()
}
fish_images = {
    1 : pygame.image.load('Images/fish/fish_1.png').convert_alpha(),
    2 : pygame.image.load('Images/fish/fish_2.png').convert_alpha(),
    3 : pygame.image.load('Images/fish/fish_3.png').convert_alpha()
}
current_angle = 0
current_direction = pygame.K_d
first_movement = False
current_time = 0
update_position = False
start_time = 0
frame_counter = 0
animation_frame = 1
movement_direction = pygame.K_d
fish_eaten = False
fish_spawned = False
shark_path = []
shark_tail_fish = []
path_length = 3
move_tail = False
fish_number = 1

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key in movement_dictionary:
                if event.key != movement_dictionary[movement_direction][2]:
                    movement_direction = event.key
                if first_movement == False:
                    pygame.time.set_timer(shark_movement, 250)
                    first_movement = True
        if event.type == shark_movement:
            shark_coordinates[0] += movement_dictionary[movement_direction][0][0]
            shark_coordinates[1] += movement_dictionary[movement_direction][0][1]
            shark_path.append((shark_coordinates[0], shark_coordinates[1]))
            target_angle = movement_dictionary[movement_direction][1]
            movement = True
            start_time = pygame.time.get_ticks()
            update_position = True
            move_tail = True

    frame_counter += 1

    current_time = (pygame.time.get_ticks() - start_time)
    if current_time > 250:
        current_time = 250

    screen.blit(checkerboard, (0, 0))

    #shark
    #animation
    if frame_counter % 10 == 0:
        animation_frame = (frame_counter // 10)
        shark = pygame.transform.scale_by(animation_frames[animation_frame], 0.5)
        shark = pygame.transform.rotate(shark, current_angle)
    #movement
    if movement:
        if current_angle != target_angle:
            current_angle = target_angle
            shark = pygame.transform.scale_by(original_shark, 0.5)
            shark = pygame.transform.rotate(shark, target_angle)
            shark_rectangle = shark.get_rect(center=shark_rectangle.center)
        shark_target[0] = ((shark_coordinates[0] * 65) - 20)
        shark_target[1] = ((shark_coordinates[1] * 65) - 20)
        movement = False
    if update_position:
        shark_start = pygame.Vector2(shark_rectangle.center)
        update_position = False
    else:
        shark_rectangle.center = shark_start.lerp(shark_target, (current_time / 250))
    screen.blit(shark, shark_rectangle)
    #tail
    if fish_eaten:
        path_length = (len(shark_tail) + 3)
        shark_tail_fish.append(fish_images[fish_number])
        path_index = (len(shark_path) - 2)
        new_x_coordinate, new_y_coordinate = shark_path[path_index]
        shark_tail.append((new_x_coordinate, new_y_coordinate))
        fish_eaten = False
    #moves the tail
    if len(shark_tail) > 0 and move_tail:
        move_tail = False
        temp_shark_tail = []
        for tail_segment in range(len(shark_tail)):
            tail_creation_index = (len(shark_path) - (tail_segment + 3))
            temp_shark_tail.append(shark_path[tail_creation_index])
        shark_tail = deepcopy(temp_shark_tail)
    #draws the tail
    for tail_number in range(len(shark_tail)):
        fish = pygame.transform.scale_by(shark_tail_fish[tail_number], 0.04)
        tail_rectangle = fish.get_rect(center = (((shark_tail[tail_number][0] * 65) - 20), ((shark_tail[tail_number][1] * 65) - 20)))
        screen.blit(fish, tail_rectangle)

    #fish
    if fish_spawned:
        if fish_x == shark_coordinates[0] and fish_y == shark_coordinates[1]:
            fish_eaten = True
            fish_spawned = False
    if fish_spawned == False:
        while True:
            fish_x = randint(1, 12)
            fish_y = randint(1, 12)
            #makes sure the fish doesn't spawn on the shark
            if fish_x == shark_coordinates[0] and fish_y == shark_coordinates[1]:
                pass
            elif (fish_x, fish_y) in shark_tail:
                pass
            else:
                fish_x_draw = ((fish_x * 65) - 20)
                fish_y_draw = ((fish_y * 65) - 20)
                fish_number = randint(1,3)
                fish = pygame.transform.scale_by(fish_images[fish_number], 0.04)
                fish_rectangle.center = (fish_x_draw, fish_y_draw)
                fish_spawned = True
                break
    screen.blit(fish, fish_rectangle)
    #print(shark_tail)
    #cuts the shark path to the desired length
    while len(shark_path) > path_length:
        shark_path.pop(0)

    #edge of map detection
    if shark_coordinates[0] > 12 or shark_coordinates[1] > 12 or shark_coordinates[0] < 0 or shark_coordinates[1] < 0:
        print("You hit the wall!")
        pygame.quit()
        exit()
    #tail detection
    if (shark_coordinates[0], shark_coordinates[1]) in shark_tail:
        print("You hit your tail!")
        pygame.quit()
        exit()
    #game win detection
    if len(shark_tail) >= 130:
        print("You win!")
        pygame.quit()
        exit()

    pygame.display.update()
    clock.tick(60)
    if frame_counter == 60:
        frame_counter = 0
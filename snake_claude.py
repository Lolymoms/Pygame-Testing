# =====================================================================
# SNAKE (Shark and Fish edition) - a heavily commented version
# =====================================================================
# How the game works, in plain English:
#   * The board is a 12 x 12 grid of squares. Each square is 65 pixels wide.
#   * The shark (the snake's head) moves one square every 250 milliseconds.
#   * When the shark lands on the fish, the fish joins the tail and a new
#     fish appears somewhere else.
#   * The tail glides along behind the shark and each fish wiggles a bit.
#   * If the shark hits a wall or its own tail, the game is over.
#   * If you collect enough fish you win, and the tail vanishes one fish
#     at a time, from the very back up to the shark.
#   * Press R after the game has ended to play again.
#
# Controls: W = up, A = left, S = down, D = right, R = restart
#
# Your folder needs to look like this:
#   this_file.py
#   Images/snake_background.png
#   Images/shark/shark_1.png, shark_2.png, shark_3.png
#   Images/fish/fish_1.png, fish_2.png, fish_3.png
# =====================================================================

import pygame
from sys import exit            # lets us close the program cleanly
from random import randint, choice
# randint(0, 2) gives a random whole number from 0 to 2.
# choice(some_list) picks one random item out of a list.
from math import sin
# sin() is a maths function that smoothly goes up and down between -1 and 1
# as you feed it a growing number. It's perfect for wiggling things.


# ---------------------------------------------------------------------
# 1. SETTINGS
# ---------------------------------------------------------------------
# Constants are values that never change while the game runs. We write
# them in CAPITAL LETTERS so we can tell them apart from normal variables.
# Putting them at the top means you can tweak the game in one place.

WINDOW_SIZE = 806       # the window is 806 x 806 pixels
SQUARE_SIZE = 65        # each grid square is 65 pixels wide
PIXEL_OFFSET = 20       # fudge number that lines the sprites up with the background
GRID_SIZE = 12          # the playable board is 12 x 12 squares
MOVE_DELAY = 250        # milliseconds between each step of the shark
WIN_LENGTH = 130        # how many tail fish you need to win

# Win animation: one tail fish disappears every 30 milliseconds.
WIN_ERASE_DELAY = 30

# Tail wiggle settings. Try changing these numbers to see what happens!
WOBBLE_SPEED = 8        # how fast the tail fish wiggle
WOBBLE_AMOUNT = 15      # how many degrees they wiggle left and right
WOBBLE_SPREAD = 0.7     # how out-of-sync neighbouring fish are (this makes a wave)

# These two numbers are the "scale" for the sprites. 0.5 means "half
# the size of the image file", 0.04 means "4% of the size".
SHARK_SCALE = 0.5
FISH_SCALE = 0.04


# ---------------------------------------------------------------------
# 2. PYGAME SETUP
# ---------------------------------------------------------------------
pygame.init()                                           # start up pygame
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))   # make the window
clock = pygame.time.Clock()                             # used to limit the frame rate
pygame.display.set_caption('Snake')                     # text in the window's title bar

# Fonts for the "game over" text. None means "use pygame's default font".
big_font = pygame.font.Font(None, 90)
small_font = pygame.font.Font(None, 45)

# Custom events. Pygame can drop these into the event queue on a timer.
# MOVE_EVENT arrives every 250ms while playing: time to move the shark.
# WIN_EVENT arrives every 30ms during the win animation: time to remove a tail fish.
MOVE_EVENT = pygame.event.custom_type()
WIN_EVENT = pygame.event.custom_type()


# ---------------------------------------------------------------------
# 3. LOADING IMAGES
# ---------------------------------------------------------------------
# We load and resize every image ONCE here, before the game loop starts.
# Loading images is slow, so we never want to do it inside the loop.

# .convert() makes a normal image faster to draw.
# .convert_alpha() does the same but keeps see-through (transparent) parts.
background = pygame.image.load('Images/snake_background.png').convert()
background = pygame.transform.scale(background, (WINDOW_SIZE, WINDOW_SIZE))

# The shark has 3 pictures that we swap between to make it look like it
# is swimming. We put them in a list so we can pick one by its number.
# (Lists start counting at 0, so shark_frames[0] is the first picture.)
shark_frames = []
for number in range(1, 4):      # number will be 1, then 2, then 3
    image = pygame.image.load(f'Images/shark/shark_{number}.png').convert_alpha()
    image = pygame.transform.scale_by(image, SHARK_SCALE)
    shark_frames.append(image)

# The animation plays frames in this order: 1, 2, 3, 3, 2, 1, then repeats.
# These are positions in the shark_frames list, so 0 means the first picture.
ANIMATION_ORDER = [0, 1, 2, 2, 1, 0]

# Same idea for the fish. There are 3 different fish pictures.
# fish_images[0] is fish_1.png, fish_images[1] is fish_2.png and so on.
fish_images = []
for number in range(1, 4):
    image = pygame.image.load(f'Images/fish/fish_{number}.png').convert_alpha()
    image = pygame.transform.scale_by(image, FISH_SCALE)
    fish_images.append(image)


# ---------------------------------------------------------------------
# 4. DIRECTIONS
# ---------------------------------------------------------------------
# A dictionary looks things up by a "key". Here the key is a keyboard key
# (like pygame.K_d) and the value is ANOTHER dictionary holding everything
# we need to know about that direction:
#   "step"     - how much to change the shark's (x, y) grid position
#   "angle"    - how many degrees to rotate the shark picture
#   "opposite" - the key for the opposite direction (the shark can't
#                turn around 180 degrees, or it would swim into its own neck)
DIRECTIONS = {
    pygame.K_d: {"step": (1, 0),  "angle": 0,   "opposite": pygame.K_a},   # right
    pygame.K_w: {"step": (0, -1), "angle": 90,  "opposite": pygame.K_s},   # up
    pygame.K_a: {"step": (-1, 0), "angle": 180, "opposite": pygame.K_d},   # left
    pygame.K_s: {"step": (0, 1),  "angle": 270, "opposite": pygame.K_w},   # down
}


# ---------------------------------------------------------------------
# 5. HELPER FUNCTIONS
# ---------------------------------------------------------------------
# A function is a named chunk of code we can run whenever we want by
# writing its name followed by brackets.

def cell_to_pixel(cell):
    """Turn a grid position like (3, 5) into the pixel position on screen
    where the CENTER of that square is."""
    x = cell[0] * SQUARE_SIZE - PIXEL_OFFSET
    y = cell[1] * SQUARE_SIZE - PIXEL_OFFSET
    return pygame.Vector2(x, y)    # a Vector2 holds an x and a y together


def spawn_fish():
    """Pick a random empty square for the next fish.
    Returns two things: the square, and which of the 3 fish pictures to use."""
    free_cells = []
    # Go through every square on the board...
    for x in range(1, GRID_SIZE + 1):          # x goes 1 to 12
        for y in range(1, GRID_SIZE + 1):      # y goes 1 to 12
            cell = (x, y)
            # ...and keep it only if the shark isn't on it and the tail isn't on it.
            if cell != head_cell and cell not in tail_cells:
                free_cells.append(cell)
    new_cell = choice(free_cells)              # pick one at random
    new_number = randint(0, 2)                 # 0, 1 or 2 = which fish picture
    return new_cell, new_number


def reset_game():
    """Put every game variable back to how it is at the very start.
    We call this once when the program starts AND every time you press R."""

    # Normally, a variable made inside a function disappears when the function
    # ends. The word "global" says: "I want to change the variables that live
    # outside this function, not make new private ones."
    global head_cell, tail_cells, previous_tail_cells, tail_fish_numbers
    global direction, next_direction
    global state, game_over_message, score
    global fish_cell, fish_number
    global previous_head_pixel, last_move_time

    head_cell = (1, 1)            # the shark starts in the top-left square
    tail_cells = []               # grid positions of each tail fish (empty at first)
    previous_tail_cells = []      # where each tail fish was BEFORE the latest step
                                  # (we need this to slide the fish smoothly)
    tail_fish_numbers = []        # which fish picture each tail segment uses
    score = 0                     # how many fish have been eaten

    direction = pygame.K_d        # the direction the shark last moved in
    next_direction = pygame.K_d   # the direction the player wants to go next

    # The game is always in one of these states (these are just words we picked):
    #   "waiting"   - before the first key press, nothing moves yet
    #   "playing"   - the game is running
    #   "game_over" - you lost, waiting for R
    #   "winning"   - you just won and the tail is vanishing (the win animation)
    #   "won"       - the win animation is finished, waiting for R
    state = "waiting"
    game_over_message = ""

    previous_head_pixel = cell_to_pixel(head_cell)   # used for smooth movement (see below)
    last_move_time = 0                               # when the shark last stepped

    # Stop both timers. Setting a timer to 0 turns it off.
    pygame.time.set_timer(MOVE_EVENT, 0)
    pygame.time.set_timer(WIN_EVENT, 0)

    # Place the first fish.
    fish_cell, fish_number = spawn_fish()


def draw_centered_text(text, font, y):
    """Draw text in the middle of the window, at height y."""
    text_surface = font.render(text, True, (255, 255, 255))   # True = smooth edges, then a white color
    text_rectangle = text_surface.get_rect(center=(WINDOW_SIZE // 2, y))
    screen.blit(text_surface, text_rectangle)


# ---------------------------------------------------------------------
# 6. START THE GAME
# ---------------------------------------------------------------------
# A see-through black layer we draw over the board when the game ends.
# set_alpha(150) means "about 60% solid", so you can still see the board underneath.
dark_overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
dark_overlay.set_alpha(150)
dark_overlay.fill((0, 0, 0))

frame_counter = 0     # counts frames, used to animate the shark

reset_game()          # set up all the starting variables


# ---------------------------------------------------------------------
# 7. THE GAME LOOP
# ---------------------------------------------------------------------
# This loop runs about 60 times every second. Each trip around it is one
# "frame". Every frame we do three things:
#     (a) handle input and events
#     (b) draw everything
#     (c) update the display
while True:

    # -----------------------------------------------------------------
    # (a) EVENTS - things that happened since the last frame
    # -----------------------------------------------------------------
    for event in pygame.event.get():

        # The player clicked the window's X button.
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # The player pressed a key down.
        if event.type == pygame.KEYDOWN:

            # Was it one of W, A, S, D, and is the game still running?
            if event.key in DIRECTIONS and state in ("waiting", "playing"):

                # Look up this direction's "opposite" and make sure the
                # player isn't trying to turn straight back on themselves.
                # We compare to `direction` (the way the shark ACTUALLY last
                # moved), not the key they pressed most recently. That stops
                # two quick key presses from sneaking in a 180 degree turn.
                if event.key != DIRECTIONS[direction]["opposite"]:
                    next_direction = event.key

                    # The very first valid key press starts the game.
                    if state == "waiting":
                        state = "playing"
                        last_move_time = pygame.time.get_ticks()
                        # Send MOVE_EVENT every MOVE_DELAY milliseconds.
                        pygame.time.set_timer(MOVE_EVENT, MOVE_DELAY)

            # R restarts, but only if the game has ended.
            if event.key == pygame.K_r and state in ("game_over", "won"):
                reset_game()

        # The timer says it's time for the shark to take one step.
        if event.type == MOVE_EVENT and state == "playing":

            # The shark now officially faces the direction the player chose.
            direction = next_direction

            # Work out which square the shark is about to move into.
            step_x, step_y = DIRECTIONS[direction]["step"]   # unpack the (x, y) pair into two variables
            new_head = (head_cell[0] + step_x, head_cell[1] + step_y)

            # --- Did we hit a wall? ---
            # The board squares are numbered 1 to 12, so 0 and 13 are outside.
            if (new_head[0] < 1 or new_head[0] > GRID_SIZE or
                    new_head[1] < 1 or new_head[1] > GRID_SIZE):
                state = "game_over"
                game_over_message = "You hit the wall!"
                pygame.time.set_timer(MOVE_EVENT, 0)    # stop the timer

            # --- Did we hit our own tail? ---
            elif new_head in tail_cells:
                state = "game_over"
                game_over_message = "You hit your tail!"
                pygame.time.set_timer(MOVE_EVENT, 0)

            # --- Otherwise it's a safe move, so do it. ---
            else:
                # Remember where everything WAS, so we can slide smoothly
                # from the old squares to the new ones when drawing.
                previous_head_pixel = cell_to_pixel(head_cell)
                previous_tail_cells = tail_cells.copy()   # .copy() makes a separate copy of the list
                last_move_time = pygame.time.get_ticks()

                # The tail follows the head. The trick: put the head's old
                # square at the FRONT of the tail list...
                tail_cells.insert(0, head_cell)
                # ...then move the head into its new square.
                head_cell = new_head

                if head_cell == fish_cell:
                    # We ate the fish! We keep the extra tail square we just
                    # added, so the tail is now one longer. We also remember
                    # which fish picture it should use.
                    tail_fish_numbers.append(fish_number)
                    score += 1

                    # The new fish at the back of the tail has nowhere to
                    # slide from, so it just starts out in its final square.
                    previous_tail_cells.append(tail_cells[-1])   # [-1] means "the last item"

                    if len(tail_cells) >= WIN_LENGTH:
                        # You win! Start the win animation.
                        state = "winning"
                        game_over_message = "You win!"
                        pygame.time.set_timer(MOVE_EVENT, 0)                 # shark stops
                        pygame.time.set_timer(WIN_EVENT, WIN_ERASE_DELAY)    # start removing fish
                    else:
                        fish_cell, fish_number = spawn_fish()
                else:
                    # We did NOT eat. Remove the LAST tail square so the
                    # tail stays the same length. Adding one at the front and
                    # removing one from the back makes the tail "slide" along.
                    tail_cells.pop()

        # WIN ANIMATION: every 30ms, remove the last fish of the tail.
        # Because the back of the tail is the END of the list, the fish
        # vanish from the back all the way up to the shark.
        if event.type == WIN_EVENT and state == "winning":
            if len(tail_cells) > 0:
                tail_cells.pop()
                previous_tail_cells.pop()      # keep the lists the same length
                tail_fish_numbers.pop()
            if len(tail_cells) == 0:
                # The whole tail is gone. The animation is finished.
                state = "won"
                pygame.time.set_timer(WIN_EVENT, 0)

    # -----------------------------------------------------------------
    # (b) DRAWING
    # -----------------------------------------------------------------
    # Things drawn later appear on top of things drawn earlier, so the
    # order here matters: background first, then fish, then tail, and
    # the shark LAST so it is always in front of its tail.

    frame_counter += 1

    # Some numbers we need for the tail AND the shark, so we work them out first.

    # How far through the current step are we? 0 means "just started" and
    # 1 means "arrived". We divide the time since the last step by the
    # step length, and cap it at 1 so it never overshoots.
    time_since_move = pygame.time.get_ticks() - last_move_time
    progress = time_since_move / MOVE_DELAY
    if progress > 1:
        progress = 1

    # Time in seconds since the program started. Used for the tail wiggle.
    seconds = pygame.time.get_ticks() / 1000

    # Background
    screen.blit(background, (0, 0))      # blit = "paste this picture at this position"

    # The fish on the board (hidden while you're winning, since you've won)
    if state not in ("winning", "won"):
        fish_rectangle = fish_images[fish_number].get_rect(center=cell_to_pixel(fish_cell))
        screen.blit(fish_images[fish_number], fish_rectangle)

    # The tail. range(len(tail_cells)) gives 0, 1, 2, ... up to the tail length.
    for index in range(len(tail_cells)):

        # 1) Glide: each fish slides from the square it was in to the square
        #    it is moving to, using the same `progress` as the shark. So the
        #    tail stays one square behind the shark instead of jumping onto it.
        start_pixel = cell_to_pixel(previous_tail_cells[index])
        end_pixel = cell_to_pixel(tail_cells[index])
        tail_pixel = start_pixel.lerp(end_pixel, progress)

        # 2) Wiggle: sin() swings between -1 and 1 as `seconds` grows, so
        #    multiplying by WOBBLE_AMOUNT gives an angle that swings left and
        #    right. Adding `index * WOBBLE_SPREAD` gives every fish a different
        #    starting point in the swing, which makes a wave run down the tail.
        wobble_angle = sin(seconds * WOBBLE_SPEED + index * WOBBLE_SPREAD) * WOBBLE_AMOUNT

        # 3) Rotate this fish's picture by that angle and draw it.
        tail_image = pygame.transform.rotate(fish_images[tail_fish_numbers[index]], wobble_angle)
        tail_rectangle = tail_image.get_rect(center=tail_pixel)
        screen.blit(tail_image, tail_rectangle)

    # The shark.
    # 1) lerp ("linear interpolation") finds the point part of the way between
    #    two points. progress 0 = the old square, 0.5 = halfway, 1 = the new square.
    #    This is what makes the shark glide instead of jumping.
    head_pixel = previous_head_pixel.lerp(cell_to_pixel(head_cell), progress)

    # 2) Pick which swimming picture to show. frame_counter // 10 changes
    #    every 10 frames (// means "divide and drop the decimal"), and % 6 makes
    #    it wrap back to 0 after 5, so we cycle through ANIMATION_ORDER forever.
    animation_step = (frame_counter // 10) % len(ANIMATION_ORDER)
    shark_image = shark_frames[ANIMATION_ORDER[animation_step]]

    # 3) Turn the picture to face the way we're swimming.
    shark_image = pygame.transform.rotate(shark_image, DIRECTIONS[direction]["angle"])

    # 4) Rotating changes the picture's size, so we make a fresh rectangle
    #    centered on the shark's position and draw it there.
    shark_rectangle = shark_image.get_rect(center=head_pixel)
    screen.blit(shark_image, shark_rectangle)

    # Game over / win screen drawn on top of everything else.
    if state in ("game_over", "won"):
        screen.blit(dark_overlay, (0, 0))
        draw_centered_text(game_over_message, big_font, WINDOW_SIZE // 2 - 50)
        draw_centered_text(f"Fish eaten: {score}", small_font, WINDOW_SIZE // 2 + 20)
        draw_centered_text("Press R to play again", small_font, WINDOW_SIZE // 2 + 70)

    # -----------------------------------------------------------------
    # (c) SHOW THE FRAME
    # -----------------------------------------------------------------
    pygame.display.update()    # actually put everything we drew onto the screen
    clock.tick(60)             # wait so the loop runs at most 60 times per second
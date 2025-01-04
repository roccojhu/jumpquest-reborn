# import modules
import os
import random
import math
import pygame

# the os modules are used to dynamically up sprite sheets
# avoids need to manually import png files of game assets
from os import listdir
from os.path import isfile, join

# import helper functions

from utils import flip, get_background, draw, handle_vertical_collision, handle_move, collide, show_victory_screen

from classes import Player, Object, Block, Fire, Flag


# initializes pygame module
pygame.init()

# sets the caption at the top of the window
pygame.display.set_caption("Jump Quest Reloaded")

## global variables are already defined in 
## utils.py. They are printed here again to enhance code comprehension
BG_COLOUR = (255, 255, 255)
# game window size
WIDTH, HEIGHT = 1000, 800
# frames per second for the game
FPS = 60
# player movespeed, defined in pixels per second
PLAYER_VEL = 5

# creates the game window using pygame module
window = pygame.display.set_mode((WIDTH, HEIGHT))


def main(window):
    ## Load main variables
    # create game clock that will tick
    clock = pygame.time.Clock()

    # load music
    pygame.mixer.music.load("assets/Music/whittingham_asturias.wav")
    # start the music. The -1 parameter loops the music continuously until game ends
    pygame.mixer.music.play(-1)
    # create background
    background, bg_image = get_background("Brown.png")
    # define the block size in pixels of game objects incl. tiles
    block_size = 96
    # create player
    player = Player(100, 100, 50, 50) # pass in x, y, width and height

    # create fire
    fire = Fire(200, HEIGHT - block_size - 64, 16, 32) # change from 100 to 200
    fire.on()

    ## Make the map, which is represented as a list of items 
    ##  We make the floor first before adding it as an object
    ## to a list of other objects
    # make the floor
  
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) 
             for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    
    # make the flag
    
    flag = Flag(block_size * 3, HEIGHT - block_size * 7 - 64, 32, 64)  # Position the flag at (700, ground level - height)

    # the * breaks down floor into its individual elements and passes them inside the of objects
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size*3, HEIGHT - block_size * 4, block_size), 
               fire,
               Block(0, HEIGHT - block_size * 6, block_size),
               Block(block_size*3, HEIGHT - block_size * 7, block_size),
               flag]
    # define parameters for scrolling window
    offset_x = 0
    scroll_area_width = 200

    # create a boolean variable to determine whether game has ended
    run = True
    while run:
        clock.tick(FPS)  # ensure the while loop runs 60 times per second

        for event in pygame.event.get():
            # first event to check is if user has quit
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        # call the player loop function. This is the one that actually moves the player
        # every single frame.
        player.loop(FPS)

        # animates the fire. No need for FPS
        fire.loop()
        # handle the move *before* drawing the map
        handle_move(player, objects) 
        # draws the background
        draw(window, background, bg_image, player, objects, offset_x) # don't forget to add player in draw function

        # checking both to the left and to the right, for correct offsetting
        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel <0):
            offset_x += player.x_vel

        # Reset the player when health reaches zero
        if player.current_health <= 0:
            player.reset_to_spawn()

    pygame.quit()  # quits the pygame game
    quit()  # ends the actual python program


if __name__ == "__main__":
    main(window)

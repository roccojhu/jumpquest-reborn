import pygame
from os import listdir
from os.path import isfile, join


## define global variables
# background colour in RGB
BG_COLOUR = (255, 255, 255)
# game window size
WIDTH, HEIGHT = 1000, 800
# frames per second for the game
FPS = 60
# player movespeed, defined in pixels per second
PLAYER_VEL = 5

# creates the game window using pygame module
window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):

    '''Since our sprite sheets have our sprites only facing on direction
    We need a function to transform and flip them if we want sprites facing
    both directions'''

    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False): # so we can load other images that aren't our main character

    '''
    '''
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha() # convert_alpha sets background transparent

    # now we need to get all the sprites in the sprite sheet
        sprites = []
        
        for i in range(sprite_sheet.get_width() // width):
            # Creates a surface that is the size of our intended animation frame, and 'blits' it onto the surface
            # We grab the animation picture, and then draw it onto this surface, then we export the surface
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32) # load transparent images, 32 is depth
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface)) # we double the animations in size

        # if we want a multi-directional animation, then we need to add two keys to our dictionary
        # for every one of our animations
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)

        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)

    # (96, 0) for the green block in the png
    # (96, 64) for the red block
    rect = pygame.Rect(96, 64, size, size) # 96,0 gives the pixel coordinates of the top left hand of block in the terrain png
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_background(name):
    """This function generates a background for the game
    Input: tile.png files from assets/Background
    Output: An array of tiles based on the size of the screen

    name: capitalised colour of background, corresponds to PNG name
    """
    image = pygame.image.load(join("assets", "Background", name))

    # get_rect returns x coord, y coord, width and height of the asset tile, in pixels
    # we use _ and _ to store the coords since they are redundant
    _, _, width, height = image.get_rect()
    tiles = []  # loop through how many tiles we need

    for i in range(
        WIDTH // width + 1
    ):  # integer division tells you how many tiles you need in X
        # print(i)
        for j in range(HEIGHT // height + 1):
            # print(j)
            pos = (
                i * width,
                j * height,
            )  # tuple of accurate positions needed for every tile
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    """Function for drawing the background itself"""

    # loops through every tile we have and draw the tile
    # at that position, which will fill the screen with tiles
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):

    '''This prevents the character from falling through blocks, and enables walking on them'''
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    ''' This function is required to handle the edge case where the player Sprite
    instantly pops up a adjacent block due to a gravity-contact glitch
    '''
    player.move(dx, 0) # starts by moving my player
    player.update() # need to update the rectangle in the mask
    collided_object = None 
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collided_object

def show_victory_screen():
    """Displays a victory message and waits before exiting."""
    font = pygame.font.Font(None, 64)
    victory_text = font.render("You Win!", True, (0, 255, 0))  # Green victory text
    window.fill((0, 0, 0))  # Clear the screen with black
    window.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - victory_text.get_height() // 2))
    pygame.display.update()
    pygame.time.delay(3000)  # Wait for 3 seconds


def handle_move(player, objects):

    ''' This function handles both movements and collisions 
    '''
        
    keys = pygame.key.get_pressed()
    # If we don't set player velocity to 0. Otherwise, the player will continually
    # move left after the left button is pressed. We don't want that.
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL)
    collide_right = collide(player, objects, PLAYER_VEL)
    
    if keys[pygame.K_LEFT] and not collide_left: # if the player hits the left key
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right: # if the player hits the right key
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:

        if obj and obj.name == "fire":
            player.make_hit()
            player.current_health -= 1  # Reduce health by 1
            player.current_health = max(0, player.current_health)  # Prevent negative health

        elif obj and obj.name == "flag": # Victory Condition
            show_victory_screen()
            pygame.quit()
            quit()

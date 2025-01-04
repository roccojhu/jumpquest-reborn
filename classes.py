import pygame
from os.path import isfile, join

from utils import load_sprite_sheets, get_block, collide, show_victory_screen

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.spawn_x = x  # Store the original spawn x-coordinate
        self.spawn_y = y  # Store the original spawn y-coordinate
        self.rect = pygame.Rect(x, y, width, height) # in pygame a rect is just a tuple for 4 values
        self.x_vel = 0 # denotes how fast we are moving player every frame laterally
        self.y_vel = 0 # denotes how fast we are moving vertically, every frame
        self.mask = None
        self.direction = "left"  # character starts facing left
        self.animation_count = 0 # reset the count when we are changing animation frames
        self.fall_count = 0 # for keeping track of character fall
        self.jump_count = 0 # for keeping track of character jump
        self.hit = False    # keep track of whether character is hit or not
        self.hit_count = 0  # hit count
        self.max_health = 3 # number of maximum health points
        self.current_health = 3 # number of current health points
        self.font = pygame.font.Font(None, 24) # self font.

    def jump(self):
        ''' This method implements jumping for the character.
        '''
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1

        # we need to make sure that as soon as the character jumps
        # it needs to get rid of any gravity already obtained
        if self.jump_count == 1:
            self.fall_count = 0


    def move(self, dx, dy):

        ''' This method defines overall movement for the player object 
        ''' 
        self.rect.x += dx
        self.rect.y += dy


    def move_left(self, vel):

        ''' This method defines left movement
        note that -= vel is used because moving left corresponds to 
        moving in the negative x-axis in the pygame coordinate world
        '''
        self.x_vel -= vel

        # checks if the character is facing the direction of movement
        if self.direction != "left": # if the character isnt facing left, make it face left
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        '''This method moves the player right'''

        self.x_vel = vel
        # checks if the character is facing right
        if self.direction != "right": 
            self.direction = "right"
            self.animation_count = 0

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def loop(self, fps):
        '''  This function actually moves the player
        This is also where gravity is added
        Keeps track of how long player is falling, in order to increase velocity
        i.e. how quickly we should be accelerating downwards
        '''
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY) # gravity fall rate
        # update character based on x and y velocity
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def reset_to_spawn(self):
        """Reset the player's position and health to the original spawn point."""
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.current_health = self.max_health
        self.x_vel = 0
        self.y_vel = 0
        self.hit = False
        self.hit_count = 0
        self.fall_count = 0
        self.jump_count = 0

    def update_sprite(self):
        sprite_sheet = "idle"

        if self.hit:
            sprite_sheet = "hit"

        # moving up
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"

            elif self.jump_count == 2:
                sprite_sheet = "double_jump"

        elif self.y_vel > self.GRAVITY * 2: # self.GRAVITY * 2 prevents glitching due to always falling even when stationary
            sprite_sheet = "fall"
        elif self.x_vel != 0:   # if sprite has some velocity in the x_direction, then it is running
            sprite_sheet = "run"

        # the following few lines of code are for animating the sprite to give it a dynamic feel even while stationary
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        # Now we want to animate the sprite, to do this we need to define a new variable
        self.update()

    def update(self):

        ''' This method updates the player object and casts it onto the pygame mask object'''
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # sprites inherit the mask property
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        ''' This method draws the player and the health bar
        '''

        # This draws the player
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

        # Draw the health bar background (red)
        health_bar_bg_rect = pygame.Rect(self.rect.x - offset_x, self.rect.y - 20, self.rect.width, 5)
        pygame.draw.rect(win, (255, 0, 0), health_bar_bg_rect)

        # Draw the current health bar (green)
        current_health_width = (self.current_health / self.max_health) * self.rect.width
        health_bar_rect = pygame.Rect(self.rect.x - offset_x, self.rect.y - 20, current_health_width, 5)
        pygame.draw.rect(win, (0, 255, 0), health_bar_rect)

        # Render the health text
        health_text = self.font.render(f"{self.current_health}/{self.max_health}", True, (0, 0, 0))
        win.blit(health_text, (self.rect.x - offset_x, self.rect.y - 35))  # Position above the player



class Object(pygame.sprite.Sprite):

    '''This class defines a generic sprite object.
    We create a rectangle. We have an image
    '''
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    ''' This creates a child class of Object which will be the blocks
    of the map of our game
    '''
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):

    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        print(self.fire)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on" # the fire pngs are named "hit", "on", "off" etc.
    
    def off(self):
        self.animation_name = "off"

    def loop(self):
        # Get the sprite sheets. But instead of trying to get sprite sheets
        # but instead of getting sprite sheets, we get the animation name
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        # instead of defining an update method here, we just copy paste
        # the update method in the Player Class. Update rectangle and mask
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        # sprites inherit the mask property
        self.mask = pygame.mask.from_surface(self.image)

        # Here is some code to prevent the animation count from getting too large

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Flag(Object):
    """A class representing the Flag that ends the game in victory."""

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "flag")
        # Load the flag image
        flag_image_path = join("assets", "Items", "Checkpoints", "flag.png")
        self.image = pygame.image.load(flag_image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))  # Resize to fit dimensions
        self.mask = pygame.mask.from_surface(self.image)  # Create a mask for collision detection
        

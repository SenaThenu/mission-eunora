import pygame
from os import listdir
from os.path import join
import math
import random
from levels import *

pygame.init()

# Game Variables
WIDTH, HEIGHT = 1250, 750
FPS = 30
OFFSET_X = 0
BLACK = (0, 0, 0)
PLAYER_VEL = 5
BG_COLOR = "Green"

# Window Customisation
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mission Eunora")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)


def flip(imgs):
    ouput_lis = []

    for img in imgs:
        ouput_lis.append(pygame.transform.flip(img, True, False))

    return ouput_lis


def load_sprites(path, width, height, rotations=False, direction=None):
    files = [f for f in listdir(path)]

    sprites = {}

    oppo_dirs = {"left": "right",
                 "right": "left"}

    for file in files:
        sprite_sheet = pygame.image.load(join(path, file))
        image_lis = []
        file_name = file.replace(".png", "")

        if rotations:
            for i in range(sprite_sheet.get_width()//width):
                frame = pygame.Surface((width, height), pygame.SRCALPHA)
                area_rect = pygame.Rect(i*width, 0, width, height)
                frame.blit(sprite_sheet, (0, 0), area_rect)
                image_lis.append(pygame.transform.scale2x(frame))

                sprites[f"{file_name}_{direction}"] = image_lis
                sprites[f"{file_name}_{oppo_dirs.get(direction)}"] = flip(
                    image_lis)

        else:
            for i in range(sprite_sheet.get_width()//width):
                frame = pygame.Surface((width, height), pygame.SRCALPHA)
                area_rect = pygame.Rect(i*width, 0, width, height)
                frame.blit(sprite_sheet, (0, 0), area_rect)
                image_lis.append(pygame.transform.scale2x(frame))
                sprites[file_name] = image_lis
    return sprites


class Player:
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width*2, height*2)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        path = join("Assets", "MainCharacters", name)
        self.SPRITES = load_sprites(path, width, height, True, self.direction)
        self.sprite = None
        self.state = "Idle"
        self.animation_count = 0
        self.GRAVITY = self.reset_gravity()
        self.mask = None
        self.jump_count = 0
        self.let_move = True

    def reset_gravity(self):
        gravity = 1
        return gravity

    def move(self):
        # if self.let_move:
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def move_right(self):
        self.x_vel = PLAYER_VEL
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def move_left(self):
        self.x_vel = -PLAYER_VEL
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def jump(self):
        self.jump_count += 1
        self.GRAVITY = self.reset_gravity()
        if self.jump_count == 1:
            self.y_vel += -self.GRAVITY * 25
        else:
            pass

    def update_state(self):
        if self.y_vel < 0:
            self.state = "Jump"
        elif self.x_vel != 0:
            self.state = "Run"
        elif self.y_vel > 2:
            self.state = "Fall"
        else:
            self.state = "Idle"
        self.animation_count += 1
        sprite_sheet = self.SPRITES[f"{self.state}_{self.direction}"]
        sprite_num = (self.animation_count //
                      self.ANIMATION_DELAY) % len(sprite_sheet)
        self.sprite = sprite_sheet[sprite_num]

    def landed(self, obj):
        self.y_vel = 0
        self.GRAVITY = 0
        self.jump_count = 0
        self.rect.bottom = obj.rect.top

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def hit_head(self):
        self.y_vel *= -1

    def loop(self):
        self.y_vel += self.GRAVITY
        self.update_state()
        self.update()

    def draw(self):
        self.move()
        WIN.blit(self.sprite, (self.rect.x + OFFSET_X, self.rect.y))


class Objects(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self):
        WIN.blit(self.image, (self.rect.x + OFFSET_X, self.rect.y))


class Block(Objects):
    def __init__(self, x, y, side):
        super().__init__(x, y, side, side, "Block")
        skin = self.load_block()
        self.image.blit(skin, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def load_block(self):
        self.skin_name = "Pinky"
        path = join("Assets", "Terrain", f"{self.skin_name}.png")
        return pygame.transform.scale2x(pygame.image.load(path))


def collide(player, floor, dx):
    collided_obj = None
    player.rect.x += dx
    player.update()
    for obj in floor:
        #obj.rect.x += OFFSET_X
        if pygame.sprite.collide_mask(player, obj):
            collided_obj = obj
            #obj.rect.x -= OFFSET_X
            break
        else:
            pass
        #obj.rect.x -= OFFSET_X
    player.rect.x -= dx
    player.update()
    return collided_obj


def handle_player(player, floor):
    player.x_vel = 0
    keys = pygame.key.get_pressed()

    right_collide = collide(player, floor, PLAYER_VEL)
    left_collide = collide(player, floor, -PLAYER_VEL)

    if keys[pygame.K_RIGHT] and not right_collide:
        player.move_right()
    if keys[pygame.K_LEFT] and not left_collide:
        player.move_left()
    if keys[pygame.K_SPACE]:
        player.jump()

    handle_verti_collision(player, floor)


def handle_verti_collision(player, objects):
    collided_objects = []
    on_floor = False
    player.rect.y += player.y_vel

    for obj in objects:
        #obj.rect.x += OFFSET_X
        if pygame.sprite.collide_mask(player, obj):
            if player.y_vel > 0:
                player.landed(obj)
                on_floor = True
            else:
                player.hit_head()
            collided_objects.append(obj)
        #obj.rect.x -= OFFSET_X
    if not on_floor:
        player.GRAVITY = 1
    player.rect.y -= player.y_vel
    return collided_objects, on_floor


def scroll_bg(player):
    global OFFSET_X
    keys = pygame.key.get_pressed()
    if (player.rect.x + OFFSET_X) > WIDTH - 190 and player.direction == "right":
        if keys[pygame.K_RIGHT]:
            OFFSET_X -= PLAYER_VEL
        #player.let_move = False

    elif (player.rect.x + OFFSET_X) < 100 and player.direction == "left":
        if keys[pygame.K_LEFT]:
            OFFSET_X += PLAYER_VEL
        #player.let_move = False

    else:
        #player.let_move = True
        pass


def generate_bg():
    path = join("Assets", "Background", f"{BG_COLOR}.png")
    piece = pygame.image.load(path)
    for col in range(math.ceil(WIDTH/piece.get_width())):
        for row in range(math.ceil(HEIGHT/piece.get_height())):
            WIN.blit(piece, (col*piece.get_height(), row*piece.get_width()))


def draw(player, floor):
    generate_bg()

    player.draw()

    # The Floor

    for block in floor:
        block.draw()

    pygame.display.update()


def game_code(player, floor):

    player.loop()
    handle_player(player, floor)
    scroll_bg(player)
    draw(player, floor)


def main():
    run = True
    clock = pygame.time.Clock()

    level, floor = set_level(Block, WIDTH, HEIGHT)

    # Classes
    block_side = 96

    player = Player(500, 0, 32, 32, "Mask Dude")

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # if menu.IS_MENU:
            #menu.draw(pygame, WIN, icon, WIDTH, HEIGHT)
        # else:
        game_code(player, floor)


if __name__ == "__main__":
    main()

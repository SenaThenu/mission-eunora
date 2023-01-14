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
        self.jump_vel = 25
        self.direction = "right"
        path = join("Assets", "MainCharacters", name)
        self.SPRITES = load_sprites(path, width, height, True, self.direction)
        self.sprite = None
        self.state = "Idle"
        self.animation_count = 0
        self.GRAVITY = self.reset_gravity()
        self.mask = None
        self.jump_count = 0

    def reset_gravity(self):
        gravity = 1
        return gravity

    def move(self):
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
            self.y_vel += -self.GRAVITY * self.jump_vel
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

    def update_skin(self):
        pass


class Fruit(Objects):
    def __init__(self, x, y, side, name):
        super().__init__(x, y, side, side, name)
        self.frames, self.vanished, self.n_sprites = self.load_img()
        self.count = 0
        self.under_collection = False
        self.collected = False
        self.delete = False

    def update_skin(self):
        if not self.under_collection:
            self.image = self.frames[self.count]
            self.count += 1
            if self.count >= self.n_sprites:
                self.count = 0
        else:
            self.image = self.vanished[self.count]
            self.count += 1
            if self.count > 5:
                self.collected = True
        self.mask = pygame.mask.from_surface(self.image)

    def load_img(self):
        path = join("Assets", "Items", "Fruits", f"{self.name}.png")
        frames = []
        sprite_sheet = pygame.image.load(path)
        n_sprites = int(sprite_sheet.get_width() /
                        sprite_sheet.get_height())
        for i in range(n_sprites):
            surface = pygame.Surface(
                (self.width/2, self.height/2), pygame.SRCALPHA)
            area_rect = pygame.Rect(
                i*sprite_sheet.get_height(), 0, self.width, self.height)
            surface.blit(sprite_sheet, (0, 0), area_rect)
            frames.append(pygame.transform.scale2x(surface))
        vanished = []
        path = join("Assets", "Items", "Fruits", "Collected.png")
        vanished_sheet = pygame.image.load(path)
        for i in range(vanished_sheet.get_width()//vanished_sheet.get_height()):
            surface = pygame.Surface(
                (vanished_sheet.get_height(), vanished_sheet.get_height()), pygame.SRCALPHA)
            area_rect = pygame.Rect(
                i*vanished_sheet.get_height(), 0, self.width, self.height)
            surface.blit(vanished_sheet, (0, 0), area_rect)
            vanished.append(pygame.transform.scale2x(surface))
        return frames, vanished, n_sprites


def handle_verti_collision(player, objects):
    collided_obj = None
    on_objects = False
    player.rect.y += player.y_vel

    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if obj.name == "Block":
                if player.y_vel > 0:
                    player.landed(obj)
                    on_objects = True
                    break
                else:
                    player.hit_head()
                    break
            collided_obj = obj
    if not on_objects:
        player.GRAVITY = 1
    player.rect.y -= player.y_vel
    return collided_obj


def collide(player, objects, dx, fruit_names):
    collided_obj = None
    player.rect.x += dx
    player.update()
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if obj.name in fruit_names:
                if not obj.collected:
                    collided_obj = obj
                    break
                else:
                    pass
            else:
                collided_obj = obj
                break
        else:
            pass
    player.rect.x -= dx
    player.update()
    return collided_obj


def handle_overall_collision(collided_objs, fruits_names):
    for obj in collided_objs:
        if obj != None:
            if obj.name in fruits_names:
                if obj.under_collection != True:
                    obj.under_collection = True
                    obj.count = 0
    else:
        pass


def handle_player(player, objects, fruit_names, fruits):
    player.x_vel = 0
    keys = pygame.key.get_pressed()

    right_collide = collide(player, objects, PLAYER_VEL, fruit_names)
    left_collide = collide(player, objects, -PLAYER_VEL, fruit_names)

    if keys[pygame.K_RIGHT]:
        if right_collide != None:
            if right_collide.name != "Block":
                player.move_right()
            else:
                pass
        else:
            player.move_right()
    if keys[pygame.K_LEFT]:
        if left_collide != None:
            if left_collide.name != "Block":
                player.move_left()
            else:
                pass
        else:
            player.move_left()
    if keys[pygame.K_SPACE]:
        player.jump()

    verti_collide = handle_verti_collision(player, objects)

    collided_objs = [right_collide, left_collide, verti_collide]
    handle_overall_collision(collided_objs, fruit_names)


def scroll_bg(player):
    global OFFSET_X
    keys = pygame.key.get_pressed()
    if (player.rect.x + OFFSET_X) > WIDTH - 190 and player.direction == "right":
        if keys[pygame.K_RIGHT]:
            OFFSET_X -= PLAYER_VEL

    elif (player.rect.x + OFFSET_X) < 100 and player.direction == "left":
        if keys[pygame.K_LEFT]:
            OFFSET_X += PLAYER_VEL

    else:
        pass


def generate_bg():
    path = join("Assets", "Background", f"{BG_COLOR}.png")
    piece = pygame.image.load(path)
    for col in range(math.ceil(WIDTH/piece.get_width())):
        for row in range(math.ceil(HEIGHT/piece.get_height())):
            WIN.blit(piece, (col*piece.get_height(), row*piece.get_width()))


def draw(player, objects, fruit_names, fruits):
    generate_bg()

    player.draw()

    # The objects

    for obj in objects:
        if obj.name in fruit_names:
            if not obj.collected:
                obj.update_skin()
                obj.draw()
            else:
                pass
        else:
            obj.draw()

    pygame.display.update()


def game_code(player, objects, fruit_names, fruits):

    player.loop()
    handle_player(player, objects, fruit_names, fruits)
    scroll_bg(player)
    draw(player, objects, fruit_names, fruits)


def main():
    run = True
    clock = pygame.time.Clock()

    player = Player(500, 0, 32, 32, "Mask Dude")

    # Game Objs Definition

    terrain, n_golden, sky_ward = set_level(
        Block, WIDTH, HEIGHT, player.jump_vel, player.GRAVITY)

    ordinary_fruits = ["Bananas", "Apple", "Cherries"]
    fruit_side = 64
    fruits = []
    for block in sky_ward:
        fruit = random.choice(ordinary_fruits)
        x = math.ceil(block.rect.x + (96/2 - (fruit_side/2)))
        y = block.rect.y - fruit_side
        fruits.append(Fruit(x, y, fruit_side, fruit))

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # if menu.IS_MENU:
            # menu.draw(pygame, WIN, icon, WIDTH, HEIGHT)
        # else:
        objects = [*terrain, *fruits]
        game_code(player, objects, ordinary_fruits, fruits)


if __name__ == "__main__":
    main()

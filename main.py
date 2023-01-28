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
font_path = join("Assets", "Fonts", "Sunny_Spells.otf")
FONT = pygame.font.Font(font_path, 48)
N_IN_BASKET = 3
FRUIT_COUNT = 0
GOLDEN_FRUIT_COUNT = 0
GRAVITY = 1

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
        self.health = 5
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
        global GRAVITY
        gravity = GRAVITY
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
        self.y_vel *= -self.GRAVITY
        self.jump_count = 2

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


# ToDo - Integrate enemies and collectibles
class Enemies():
    # Disappear in the direction of right
    def __init__(self, x, y, width, height, specific_name, type_name, health, coverage=200, ani_delay=0, idle=False, vel=0, can_attack=False, shoots_bullets=False, max_bullets=0, bullet_vel=0):
        self.health = health
        self.animation_delay = ani_delay

        self.width = width
        self.height = height
        self.name = type_name       # Make sure to pass the name in the Assets folder
        self.specific_name = specific_name

        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.count = 0
        self.hit = False
        self.hit_player = False

        self.starting_x = x
        self.max_reach = x + coverage
        self.min_reach = x - coverage

        self.direction = "left"

        self.idle = idle

        self.update_state()

        self.vel = vel
        self.opposite_vel = {"right": self.vel,
                             "left": -self.vel}

        self.can_attack = can_attack

        self.shoots_bullets = shoots_bullets
        self.max_bullets = max_bullets
        self.bullet_vel = bullet_vel
        self.bullet_list = []

        # Loading the sprites

        path = join("Assets", self.name, specific_name)
        self.direction = "left"
        self.sprites = load_sprites(
            path, self.width, self.height, True, self.direction)
        self.sprites["Disappear_right"] = [pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA)]

        self.image = self.sprites[f"{self.state}_{self.direction}"][self.count //
                                                                    self.animation_delay]

    def update_state(self):
        if not self.idle:
            self.state = "Walk"
        else:
            self.state = "Idle"

    def wander(self):
        if self.rect.x == self.max_reach:
            self.direction = "left"
        elif self.rect.x == self.min_reach:
            self.direction = "right"

        self.rect.x += self.opposite_vel.get(self.direction)

    def haste(self):
        if self.direction == "left":
            if self.rect.x <= self.min_reach:
                pass
            else:
                self.rect.x -= self.vel * 2
        else:
            if self.rect.x >= self.max_reach:
                pass
            else:
                self.rect.x += self.vel * 2

    def control_bullets(self, player, bullet, bullet_smash):
        if self.specific_name == "Trunk":
            bullet_x, bullet_y = HEIGHT - 96 - \
                (self.image.get_height()//2-bullet.get_height() //
                 2), self.rect.y + (self.rect.width//2)
        elif self.specific_name == "Plant":
            bullet_x, bullet_y = (
                HEIGHT - 96 - self.image.get_height()) + 20, self.rect.y + (self.rect.width // 2)

        if self.activated:
            self.bullet_list.append([pygame.Rect(
                bullet_x, bullet_y, bullet.get_width(), bullet.get_height()), 0])

        for bull in self.bullet_list:
            if self.direction == "left":
                bull[0].rect.x -= self.bullet_vel
            else:
                bull[0].rect.x += self.bullet_vel
            if bull.colliderect(player.rect):
                player.health -= 1
                WIN.blit(bullet_smash[bull[1]],
                         (bull[0].rect.x, bull[0].rect.y))
                if bull[1] != 1:
                    bull[1] += 1
            else:
                WIN.blit(bullet, (bull[0].rect.x, bull[0].rect.y))

    def in_range_activation(self, player_x, player_y):
        if player_x > self.min_reach and player_x < self.max_reach:
            if player_x < self.rect.x and player_y + 25 > self.rect.y:
                self.direction = "left"
                return True
            elif player_x > self.rect.x and player_y + 25 > self.rect.y:
                self.direction = "right"
                return True
            else:
                return False
        else:
            self.state = "Walk"

    def mark_death(self):
        if self.health <= 0:
            self.direction = "right"
            self.state = "Disappear"
            self.count = 0
            return True
        else:
            return False

    def draw(self, player):
        self.sprite_sheet = self.sprites[f"{self.state}_{self.direction}"]
        index = self.count // self.animation_delay % len(self.sprite_sheet)
        self.image = self.sprite_sheet[index]

        self.dead = self.mark_death()

        if not self.dead:
            activated = self.in_range_activation(player.rect.x, player.rect.y)

            if self.hit:
                def get_acc(acc): return (
                    self.count+1) * acc if self.direction == "left" else (self.count+1) * -acc

                self.rect.x += get_acc(15)
                if self.rect.x <= self.max_reach and self.rect.x >= self.min_reach:
                    pass
                else:
                    self.rect.x -= get_acc(15)
                if self.count >= len(self.sprite_sheet):
                    self.hit = False
                    self.count = 0

            elif not activated:
                if not self.idle:
                    self.wander()
                else:
                    pass

            else:
                if not self.idle:
                    if self.can_attack:
                        if self.state != "Hit Player" and self.state != 'Run':
                            self.state = "Run"
                            self.count = 0
                        self.haste()
                elif self.shoots_bullets:
                    self.control_bullets(
                        player, self.sprites[f"Bullet_{self.direction}"], self.sprites[f"Bullet Pieces_{self.direction}"])
                else:
                    pass

            WIN.blit(self.image, (self.rect.x + OFFSET_X, self.rect.y))
            self.count += 1
        else:
            pass


# class Collectible():
#     def __init__(self, x, y, width, height, specific_name, health, coverage=200, idle=False, vel=0, can_attack=False, shoots_bullets=False, max_bullets=0, bullet_vel=0):
#         self.width = width
#         self.height = height
#         self.health = health

#         self.animation_dealy = 1

#         self.rect = pygame.Rect(x, y, width, height)

#         self.name = "Collectible"
#         self.specific_name = specific_name

#         self.starting_x = x
#         self.max_reach = x + coverage
#         self.min_reach = x - coverage

#         self.count = 0

#         self.direction = "left"

#         self.idle = idle
#         if self.idle:
#             self.state = "Idle"
#         else:
#             self.state = "Run"
#         self.can_attack = can_attack

#         self.shoots_bullets = shoots_bullets
#         self.max_bullets = max_bullets
#         self.bullet_vel = bullet_vel
#         self.bullet_list = []

#         self.x_vel = vel

#         path = join("Assets", "ToCollect", specific_name)
#         self.sprites = load_sprites(
#             path, self.width, self.height, True, self.direction)

#         self.image = pygame.Surface((width, height), pygame.SRCALPHA)

#     def check_activation(self, player):
#         if player.rect.x > self.min_reach and player.rect.x < self.max_reach:
#             self.activated = True
#         else:
#             self.activated = False

#     def draw(self, player):
#         self.sprite_sheet = self.sprites.get(f"{self.state}_{self.direction}")
#         self.image = self.sprite_sheet[self.count //
#                                        self.animation_dealy % len(self.sprite_sheet)]

#         self.check_activation(player)

#         if not self.idle:
#             if self.direction == "left":
#                 self.rect.x -= self.x_vel
#                 if self.rect.x <= self.min_reach:
#                     self.direction = "right"
#             else:
#                 self.rect.x += self.x_vel
#                 if self.rect.x >= self.max_reach:
#                     self.direction = "left"
#                 else:
#                     pass

#         if self.can_attack:
#             self.handle_attack()
#         if self.shoots_bullets:
#             self.control_bullets(
#                 player, self.sprite_sheet[f"Bullet_{self.direction}"], self.sprite_sheet[f"Bullet_Pieces_{self.direction}"])

#         WIN.blit(self.image, (self.rect.x, self.rect.y))
#         self.count += 1


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
    global FRUIT_COUNT, N_LIVES
    for obj in collided_objs:
        if obj != None:
            if obj.name in fruits_names:
                if obj.under_collection != True:
                    obj.under_collection = True
                    obj.count = 0
                    FRUIT_COUNT += 1
    else:
        pass


def handle_player(player, objects, fruit_names):
    player.x_vel = 0
    keys = pygame.key.get_pressed()

    right_collide = collide(player, objects, PLAYER_VEL, fruit_names)
    left_collide = collide(player, objects, -PLAYER_VEL, fruit_names)
    verti_collide = handle_verti_collision(player, objects)

    # Health
    def decrease_health(collided, decrease_player_health):
        if not decrease_player_health:
            collided.health -= 1
            collided.state = "Hit"
            player.y_vel = -player.GRAVITY * 20
            collided.hit = True
            collided.count = 0
        else:
            player.health -= 1
            collided.hit = True
            collided.state = "Hit Player"
            collided.count = 0

    if right_collide != None:
        if right_collide.name == "Enemies" or right_collide.name == "Collectibles":
            if right_collide.state == "Hit":
                pass
            else:
                decrease_health(right_collide, True)
    elif left_collide != None:
        if left_collide.name == "Enemies" or left_collide.name == "Collectibles":
            if left_collide.state == "Hit":
                pass
            else:
                decrease_health(left_collide, True)
    elif verti_collide != None:
        if verti_collide.name == "Enemies" or verti_collide.name == "Collectibles":
            decrease_health(verti_collide, False)

    # Motion
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


def draw(player, objects, fruit_names):
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
        elif obj.name == "Enemies" or obj.name == "Collectibles":
            obj.draw(player)
        # elif obj.name == "Collectible":
        #     obj.draw(player)
        else:
            obj.draw()

    # Fruit Basket
    basket_path = join("Assets", "Items", "Fruits", "Basket.png")
    basket = pygame.image.load(basket_path)
    n_baskets = FRUIT_COUNT // N_IN_BASKET

    font_face = FONT.render(str(n_baskets), True, BLACK)

    WIN.blit(font_face, (WIDTH-font_face.get_width(), 0))
    WIN.blit(basket, (WIDTH-font_face.get_width()-basket.get_width(), 0))

    # Lives
    heart = pygame.image.load(join("Assets", "Items", "Heart.png"))
    font_face = FONT.render(str(player.health), True, BLACK)
    WIN.blit(heart, (0, 0))
    WIN.blit(font_face, (heart.get_width(), 0))
    pygame.display.update()

    if player.health <= 0:
        pygame.time.delay(100)
        quit()


def game_code(player, objects, fruit_names):
    player.loop()
    handle_player(player, objects, fruit_names)
    scroll_bg(player)
    draw(player, objects, fruit_names)


def main():
    run = True
    clock = pygame.time.Clock()

    player = Player(500, 0, 32, 32, "Mask Dude")

    # Game Objs Definition

    # Blocks
    terrain, n_golden, sky_ward = set_level(
        Block, WIDTH, HEIGHT, player.jump_vel, player.GRAVITY)

    # Fruits
    ordinary_fruits = ["Kiwi", "Apple", "Cherries",
                       "Bananas", "Melon", "Pineapple", "Strawberry"]
    fruit_side = 64
    fruits = []

    for block in sky_ward:
        fruit = random.choice(ordinary_fruits)
        x = math.ceil(block.rect.x + (96/2 - (fruit_side/2)))
        y = block.rect.y - fruit_side
        fruits.append(Fruit(x, y, fruit_side, fruit))

    # Enemies
    enemy_name = "Chameleon"
    if enemy_name == "Rino":
        width, height = 52, 34
    elif enemy_name == "AngryPig":
        width, height = 36, 30
    elif enemy_name == "Ghost":
        width, height = 44, 15
    elif enemy_name == "Slime":
        width, height = 44, 30
    elif enemy_name == "Rocks":
        width, height = 38, 34
    elif enemy_name == "Chameleon":
        width, height = 84, 38
    #enemy = Enemies(500, HEIGHT-96-height*2, width, height, enemy_name, 3)

    # Collectible
    to_collect = Enemies(500, HEIGHT-96-height*2, width, height,
                         enemy_name, "Collectibles", 3, 200, 3, False, 5, True)
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # if menu.IS_MENU:
            # menu.draw(pygame, WIN, icon, WIDTH, HEIGHT)
        # else:
        objects = [*terrain, *fruits, to_collect]
        game_code(player, objects, ordinary_fruits)


if __name__ == "__main__":
    main()

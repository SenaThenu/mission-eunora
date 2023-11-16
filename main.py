import pygame
from os import listdir
from os.path import join
import math
import random
from levels import *

pygame.init()

# TODO: Please fix the bug when the bullets go outta range...

# Game Variables
WIDTH, HEIGHT = 1200, 750
FPS = 30
OFFSET_X = 0
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_VEL = 5
PLAYER_HEALTH = 5

FONT = pygame.font.SysFont("Agency FB", 48)

# Physics
GRAVITY = 1
JUMP_ANGLE = 45
RESPAWN_POINTS = []
RESPAWNED = 0

GAME_OVER = False

# Fruit Stuff
f = open("fruit_count.txt", "r")
f_count = f.read()
FRUIT_COUNT = int(f_count)
# Window Customisation
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mission Eunora")
icon = pygame.image.load(join("Assets", "Icon.png"))
pygame.display.set_icon(icon)

# Defining Menus
START_MENU = True
LEVELS_MENU = False
MAP_MENU = False
GAME_START = False


def set_up_menu(name):
    global START_MENU, LEVELS_MENU, MAP_MENU, GAME_START
    if name.lower() == "start":
        START_MENU = True
        LEVELS_MENU = False
        MAP_MENU = False
        GAME_START = False
    elif name.lower() == "levels":
        START_MENU = False
        LEVELS_MENU = True
        MAP_MENU = False
        GAME_START = False
    elif name.lower() == "map":
        START_MENU = False
        LEVELS_MENU = False
        MAP_MENU = True
        GAME_START = False
    elif name.lower() == "back":
        START_MENU = True
        LEVELS_MENU = False
        MAP_MENU = False
        GAME_START = False
    elif name.lower() == "play":
        START_MENU = False
        LEVELS_MENU = False
        MAP_MENU = False
        GAME_START = True


def replay():
    set_up_menu("play")
    main()


def reset_OFFSET(custom=0):
    global OFFSET_X
    OFFSET_X = custom


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

# In Menus, only the first letter is capital...


def check_button_click(x, y, width, height, clicked):
    pressed = False
    mx, my = clicked
    if mx > x and mx < (x + width):
        if my > y and my < (y+height):
            pressed = True
    return pressed


class Menus:
    def __init__(self, space_between):
        self.space_between = space_between
        self.default_path = join("Assets", "Menus")

    def refresh_screen(self):
        pygame.time.delay(100)
        pygame.display.update()

    def set_up_button(self, name, path, pressed, y):
        bt = pygame.image.load(join(path, f"{name}_button.png"))
        bt_x, bt_y = WIDTH//2 - bt.get_width()//2, y
        bt_pressed = check_button_click(
            bt_x, y, bt.get_width(), bt.get_height(), pressed)
        if bt_pressed:
            bt = pygame.image.load(join(path, f"{name}_pressed.png"))
            set_up_menu(name)
        else:
            pass
        WIN.blit(bt, (bt_x, bt_y))
        return y + bt.get_height()

    def load_bg(self, path):
        bg = pygame.image.load(join(path, "bg.jpg"))
        WIN.blit(bg, (0, 0))

    def start(self, clicked):
        path = join(self.default_path, "Start Menu")
        self.load_bg(path)

        logo = pygame.image.load(join(path, "Logo.png"))
        logo_x, logo_y = WIDTH//2 - logo.get_width()//2, HEIGHT//2 - \
            self.space_between//2 - logo.get_height()

        WIN.blit(logo, (logo_x, logo_y))

        y = HEIGHT//2 + self.space_between//2

        y = self.set_up_button("Play", path, clicked, y)
        y = self.set_up_button("Levels", path, clicked, y+10)
        y = self.set_up_button("Map", path, clicked, y+10)

        self.refresh_screen()

    def map(self, level, clicked):
        path = join(self.default_path, "Map")
        self.load_bg(path)
        map_img = pygame.image.load(join(path, f"{level-1}.png"))
        WIN.blit(map_img, (0, 0))
        self.set_up_button("Back", path, clicked, 0)

        self.refresh_screen()

    def levels(self, level, clicked):
        path = join(self.default_path, "Levels")
        self.load_bg(path)
        level_img = pygame.image.load(join(path, f"{level}.png"))
        WIN.blit(level_img, (0, 0))
        self.set_up_button("Back", path, clicked, 0)

        self.refresh_screen()


class Player:
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width*2, height*2)
        self.health = 5
        self.x_vel = 0
        self.y_vel = 0
        self.jump_vel = 0
        self.default_jump = 15
        self.direction = "right"
        path = join("Assets", "MainCharacters", name)
        self.SPRITES = load_sprites(path, width, height, True, self.direction)
        self.sprite = None
        self.state = "Idle"
        self.animation_count = 0
        self.GRAVITY = self.reset_gravity()
        self.mask = None
        self.jump_count = 0
        self.left_arrow_press = 0
        self.right_arrow_press = 0
        self.secs_for_acc = 20
        self.hit = False

    def reset_gravity(self):
        global GRAVITY
        gravity = GRAVITY
        return gravity

    def move(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel

    def move_right(self):
        self.x_vel = PLAYER_VEL + (self.right_arrow_press // self.secs_for_acc)
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def move_left(self):
        self.x_vel = - \
            (PLAYER_VEL + (self.left_arrow_press // self.secs_for_acc))
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def jump(self):
        self.jump_vel = self.default_jump + \
            math.ceil(abs(self.x_vel) / math.cos(JUMP_ANGLE))
        self.jump_count += 1
        self.GRAVITY = self.reset_gravity()
        if self.jump_count == 1:
            self.y_vel += -self.GRAVITY * self.jump_vel
        else:
            pass

    def update_state(self):
        if not self.hit:
            if self.y_vel < 0:
                self.state = "Jump"
            elif self.x_vel != 0:
                self.state = "Run"
            elif self.y_vel > 2:
                self.state = "Fall"
            else:
                self.state = "Idle"
        else:
            if self.animation_count >= 14:
                self.hit = False
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


class Weirdies(Objects):
    def __init__(self, x, y, width, height, specific_name, functional=False, inherent="On"):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = "Weirdies"
        self.sprites = load_sprites(
            join("Assets", "Weirdies", specific_name), width, height, False)
        self.state = inherent
        self.image = self.sprites[self.state][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.count = 0
        self.functional = functional
        self.specific_name = specific_name

    def update_mask(self):
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self):
        self.sprite_sheet = self.sprites[self.state]
        self.image = self.sprite_sheet[self.count]

        WIN.blit(self.image, (self.rect.x + OFFSET_X, self.rect.y))

        self.update_mask()
        if self.functional and self.state != "Off":
            self.count += 1
        if self.count >= len(self.sprite_sheet):
            self.count = 0


class Block(Objects):
    def __init__(self, x, y, side, skin_name="Sci-Fi"):
        super().__init__(x, y, side, side, "Block")
        self.skin_name = skin_name
        skin = self.load_block()
        self.image.blit(skin, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

    def load_block(self):
        path = join("Assets", "Terrain", f"{self.skin_name}.png")
        return pygame.image.load(path)

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


class Bullet():
    def __init__(self, x, y, vel, dir, skin):
        self.vel = vel
        self.direction = dir
        self.rect = pygame.Rect(x, y, 16, 16)
        self.image = skin
        self.mask = pygame.mask.from_surface(self.image)

    def loop(self, blocks, player):
        if self.direction == "left":
            self.rect.x -= self.vel
        else:
            self.rect.x += self.vel
        if pygame.sprite.collide_mask(self, player):
            player.health -= 1
            return True
        else:
            for block in blocks:
                if pygame.sprite.collide_mask(self, block):
                    return True
                else:
                    return False


class Opps():
    def __init__(self, x, y, width, height, specific_name, type_name, health, coverage=200, ani_delay=0, idle=False, vel=0, can_attack=False, shoots_bullets=False, max_bullets=0, bullet_vel=0):
        self.health = health
        self.animation_delay = ani_delay
        self.death = False

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

        # Loading the sprites

        path = join("Assets", self.name, specific_name)
        self.direction = "left"
        self.sprites = load_sprites(
            path, self.width, self.height, True, self.direction)
        self.sprites["Disappear_right"] = [pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA)]

        self.image = self.sprites[f"{self.state}_{self.direction}"][self.count //
                                                                    self.animation_delay]
        # This is about the bullet stuff...
        self.shoots_bullets = shoots_bullets
        self.bullet_vel = bullet_vel
        self.bullet_list = []
        if self.shoots_bullets:
            self.bullet = self.sprites[f"Bullet_{self.direction}"][0]

    def update_state(self):
        if not self.idle:
            self.state = "Walk"
        else:
            self.state = "Idle"

    def wander(self):
        if self.rect.x >= self.max_reach:
            self.direction = "left"
        elif self.rect.x <= self.min_reach:
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

    def add_bullets(self):
        if self.state != "Attack":
            self.count = 0
            self.state = "Attack"

        attack_pos = 5

        if self.count // self.animation_delay == attack_pos:
            self.bullet_list.append(Bullet(
                self.rect.x, self.rect.y + 20, self.bullet_vel, self.direction, self.bullet))

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
            self.update_state()

    def mark_death(self):
        if self.health <= 0:
            self.direction = "right"
            self.state = "Disappear"
            self.count = 0
            return True
        else:
            return False

    def draw(self, player, terrain):
        self.sprite_sheet = self.sprites[f"{self.state}_{self.direction}"]
        if self.count >= len(self.sprite_sheet)*self.animation_delay:
            self.count = 0
        self.image = self.sprite_sheet[self.count//self.animation_delay]

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
                if self.shoots_bullets:
                    self.state = "Attack"

                elif self.can_attack:
                    if self.state != "Hit Player" and self.state != 'Run':
                        self.state = "Run"
                        self.count = 0
                    self.haste()
                else:
                    pass

            # Continuous blits
            if self.shoots_bullets:
                for i, bull in enumerate(self.bullet_list):
                    is_dead = bull.loop(terrain, player)
                    if is_dead:
                        self.bullet_list.pop(i)
                    else:
                        pass
                for bull in self.bullet_list:
                    WIN.blit(bull.image, (bull.rect.x + OFFSET_X, bull.rect.y))

            if self.state == "Attack":
                self.add_bullets()
            WIN.blit(self.image, (self.rect.x + OFFSET_X, self.rect.y))
            self.count += 1
        else:
            pass


class Checkpoint():
    def __init__(self, x, y, side):
        self.state = "Idle"
        self.rect = pygame.Rect(x, y, side, side)
        self.sprites = load_sprites(
            join("Assets", "Items", "Checkpoint"), side, side)
        self.image = self.sprites[self.state][0]
        self.name = "Checkpoint"
        self.mask = pygame.mask.from_surface(self.image)
        self.count = 0
        self.waved = False

    def draw(self):
        self.sprite_sheet = self.sprites[self.state]
        WIN.blit(self.sprite_sheet[self.count],
                 (self.rect.x + OFFSET_X, self.rect.y))

        if self.state == "Idle":
            self.count = 0
        else:
            self.count += 1
        if self.count >= len(self.sprites["Wave"]):
            self.state = "Idle"
            self.count = 0


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


def handle_overall_collision(collided_objs, fruits_names, player):

    def harm_player():
        if not player.hit:
            player.hit = True
            player.state = "Hit"
            player.animation_count = 0
        else:
            pass
        player.health -= 1

    global FRUIT_COUNT, N_LIVES
    for obj in collided_objs:
        if obj != None:
            if obj.name in fruits_names:
                if obj.under_collection != True:
                    obj.under_collection = True
                    obj.count = 0
                    FRUIT_COUNT += 1
            elif obj.name == "Checkpoint":
                if not obj.waved:
                    obj.state = "Wave"
                    obj.waved = True
                else:
                    pass
                RESPAWN_POINTS.append([[obj.rect.x, obj.rect.y], OFFSET_X])
            elif obj.name == "Weirdies":
                sky_rocketers = ["Fan", "Trampoline"]
                if obj.specific_name in sky_rocketers:
                    player.y_vel *= -player.GRAVITY * 2
                    player.gravity = 1
                    obj.state = "On"
                else:
                    harm_player()
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
        player.left_arrow_press = 0
        player.right_arrow_press += 1
        if right_collide != None:
            if right_collide.name != "Block":
                player.move_right()
            else:
                pass
        else:
            player.move_right()
    if keys[pygame.K_LEFT]:
        player.right_arrow_press = 0
        player.left_arrow_press += 1
        if left_collide != None:
            if left_collide.name != "Block":
                player.move_left()
            else:
                pass
        else:
            player.move_left()
    if keys[pygame.K_SPACE]:
        player.right_arrow_press /= 2
        player.left_arrow_press /= 2
        player.jump()

    collided_objs = [right_collide, left_collide, verti_collide]
    handle_overall_collision(collided_objs, fruit_names, player)


def scroll_bg(player):
    global OFFSET_X
    keys = pygame.key.get_pressed()
    if (player.rect.x + OFFSET_X) > WIDTH - 190 and player.direction == "right":
        if keys[pygame.K_RIGHT]:
            OFFSET_X -= abs(player.x_vel)

    elif (player.rect.x + OFFSET_X) < 100 and player.direction == "left":
        if keys[pygame.K_LEFT]:
            OFFSET_X += abs(player.x_vel)

    else:
        pass


def generate_bg():
    bg = pygame.image.load(join("Assets", "Background", "bg.jpg"))
    WIN.blit(bg, (0, 0))


def draw(player, objects, fruit_names, terrain, level, show_level, max_respawn, clicked):
    global RESPAWNED, GAME_OVER
    generate_bg()

    if not GAME_OVER:
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
                obj.draw(player, terrain)
            else:
                obj.draw()

        space_between = 10

        # Fruit Basket
        basket_path = join("Assets", "Items", "Fruits", "Basket.png")
        basket = pygame.image.load(basket_path)
        font_face = FONT.render(str(FRUIT_COUNT), True, WHITE)

        WIN.blit(font_face, (WIDTH-font_face.get_width(), 0))
        WIN.blit(basket, (WIDTH-font_face.get_width()-basket.get_width(), 0))
        prev_x = WIDTH - (font_face.get_width()+basket.get_width())

        # Lives
        health = pygame.image.load(
            join("Assets", "Items", "Health", f"{player.health}.png"))
        prev_x -= health.get_width() + space_between
        WIN.blit(health, (prev_x, 0))

        respawn_img = pygame.image.load(
            join("Assets", "Items", "Respawn", f"{max_respawn-RESPAWNED}.png"))
        prev_x -= respawn_img.get_width() + space_between
        WIN.blit(respawn_img, (prev_x, 0))

        if show_level:
            lev_img = pygame.image.load(
                join("Assets", "Levels", f"{level}.png"))
            WIN.blit(
                lev_img, (WIDTH//2-(lev_img.get_width()//2), lev_img.get_height()))

        # Back to the START!!!
        home_bt = pygame.image.load(join("Assets", "Menus", "Home_button.png"))

        wanna_return = check_button_click(
            0, 0, home_bt.get_width(), home_bt.get_height(), clicked)
        if wanna_return:
            set_up_menu("Start")
            home_bt = pygame.image.load(
                join("Assets", "Menus", "Home_pressed.png"))

        WIN.blit(home_bt, (0, 0))

        if player.health <= 0:
            if RESPAWNED < max_respawn:
                player.right_arrow_press, player.left_arrow_press = 0, 0
                player.health = PLAYER_HEALTH
                x_y, offset = RESPAWN_POINTS[-1]
                reset_OFFSET(offset)
                player.rect.x, player.rect.y = x_y[0], x_y[1]
                RESPAWNED += 1
            else:

                GAME_OVER = True
    else:
        game_over_path = join("Assets", "Menus", "GameOver")
        game_over_img = pygame.image.load(join(game_over_path, "Main.png"))
        g_x, g_y = WIDTH//2 - game_over_img.get_width()//2, HEIGHT//2 - \
            game_over_img.get_height()//2
        WIN.blit(game_over_img, (g_x, g_y))

    pygame.display.update()


def check_level_passed(to_collect):
    if to_collect.health <= 0:
        level_passed = True
    else:
        level_passed = False
    return level_passed


def show_victory(level):
    win_img = pygame.image.load(join("Assets", "Menus", "Win", f"{level}.png"))
    WIN.blit(win_img, (0, 0))

    pygame.display.update()
    pygame.time.delay(3000)


def game_code(player, objects, fruit_names, terrain, to_collect, level, show_level, max_respawn, clicked):
    level_passed = False
    level_passed = check_level_passed(to_collect)
    if not level_passed:
        player.loop()
        handle_player(player, objects, fruit_names)
        scroll_bg(player)
        draw(player, objects, fruit_names, terrain,
             level, show_level, max_respawn, clicked)
    else:
        level += 1
        write_file = open("level.txt", "w")
        write_file.write(str(level))
        write_file.close()
        fruit_file = open("fruit_count.txt", "w")
        fruit_file.write(str(FRUIT_COUNT))
        fruit_file.close()

        show_victory(level-1)
        main()


def main():
    global RESPAWNED
    run = True
    clock = pygame.time.Clock()

    player_spawn_x, player_spawn_y = WIDTH//2 - 32, HEIGHT//2-32
    player = Player(player_spawn_x, player_spawn_y, 32, 32, "Mask Dude")
    RESPAWN_POINTS.append([[player_spawn_x, player_spawn_y], 0])

    # Game Objs Definition

    # Blocks
    terrain, mount_blocks, fruit_blocks, to_collect, enemies, weirdies, checkpoints, level = set_level(
        Block, Opps, Checkpoint, Weirdies, WIDTH, HEIGHT)

    # Fruits
    if level <= 9:
        ordinary_fruits = ["Kiwi", "Apple", "Cherries",
                           "Bananas", "Melon", "Pineapple", "Strawberry"]
        fruit_side = 64
        fruits = []

        level_counter = 0
        level_on_air_time = 60

        for block in fruit_blocks:
            fruit = random.choice(ordinary_fruits)
            x = math.ceil(block.rect.x + ((96-fruit_side)//2))
            y = block.rect.y - fruit_side
            fruits.append(Fruit(x, y, fruit_side, fruit))

        objects = [*fruits, *weirdies, *terrain, *
                   mount_blocks, *enemies, *checkpoints, to_collect]

        RESPAWNED = 0
        reset_OFFSET()

        RESPAWN_POINTS.append([[500, 500], OFFSET_X])
        max_respawn = 3

    # MENU STUFF!!!
    menu_cls = Menus(50)
    while run:
        clock.tick(FPS)
        clicked = (0, 0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = pygame.mouse.get_pos()
        if not GAME_START:
            if START_MENU:
                menu_cls.start(clicked)
            elif LEVELS_MENU:
                menu_cls.levels(level, clicked)
            elif MAP_MENU:
                menu_cls.map(level, clicked)
        else:
            if level <= 9:
                if level_counter <= level_on_air_time:              # This means the title of the menu!
                    level_counter += 1
                    show_level = True
                else:
                    show_level = False
                game_code(player, objects, ordinary_fruits,
                          terrain, to_collect, level, show_level, max_respawn, clicked)
            else:
                generate_bg()
                complete_img = pygame.image.load(
                    join("Assets", "Menus", "Completed.png"))
                WIN.blit(complete_img, (0, 0))

                home_bt = pygame.image.load(
                    join("Assets", "Menus", "Home_button.png"))

                wanna_return = check_button_click(
                    0, 0, home_bt.get_width(), home_bt.get_height(), clicked)
                if wanna_return:
                    set_up_menu("Start")
                    home_bt = pygame.image.load(
                        join("Assets", "Menus", "Home_pressed.png"))

                WIN.blit(home_bt, (0, 0))
                pygame.display.update()


if __name__ == "__main__":
    main()

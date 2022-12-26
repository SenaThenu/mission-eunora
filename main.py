import pygame
from os import listdir
from os.path import join

pygame.init()

# Game Variables
WIDTH, HEIGHT = 1250, 750
FPS = 30
OFFSET_X = 0
BLACK = (0, 0, 0)
PLAYER_VEL = 5

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
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        path = join("Assets", "MainCharacters", name)
        self.SPRITES = load_sprites(path, width, height, True, self.direction)
        self.sprite = None
        self.state = "Idle"
        self.animation_count = 0

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

    def update(self):
        if self.y_vel == 0:
            if self.x_vel != 0:
                self.state = "Run"
            else:
                self.state = "Idle"
        self.animation_count += 1

    def loop(self):
        self.update()
        sprite_sheet = self.SPRITES[f"{self.state}_{self.direction}"]
        sprite_num = (self.animation_count //
                      self.ANIMATION_DELAY) % len(sprite_sheet)
        self.sprite = sprite_sheet[sprite_num]

    def draw(self):
        self.move()
        WIN.blit(self.sprite, (self.rect.x, self.rect.y))
        #pygame.draw.rect(WIN, BLACK, self.rect)


class Objects(pygame.sprite.Sprite):
    def __init__(self):
        pass


def handle_player(player):
    player.x_vel = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        player.move_right()
    if keys[pygame.K_LEFT]:
        player.move_left()


def scroll_bg():
    pass


def generate_bg():
    WIN.fill("White")
    pass


def draw(player):
    generate_bg()
    player.draw()
    pygame.display.update()


def game_code(player):
    # Insert the main code for the game; calling classes and that sorta stuff!
    handle_player(player)
    player.loop()
    draw(player)


def main():
    run = True
    clock = pygame.time.Clock()
    player = Player(100, 100, 32, 32, "Pink Man")
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # if menu.IS_MENU:
            #menu.draw(pygame, WIN, icon, WIDTH, HEIGHT)
        # else:
        game_code(player)


if __name__ == "__main__":
    main()

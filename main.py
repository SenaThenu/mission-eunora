import pygame
from os.path import join
import menu

pygame.init()

# Game Variables
WIDTH, HEIGHT = 1250, 750
FPS = 30
OFFSET_X = 0

# Window Customisation
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mission Eunora")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)


def load_sprites():
    pass


class Player:
    def __init__(self):
        pass


class Objects(pygame.sprite.Sprite):
    def __init__(self):
        pass


def handle_player():
    pass


def scroll_bg():
    pass


def generate_bg():
    pass


def draw():
    pygame.display.update()


def game_code():
    # Insert the main code for the game; calling classes and that sorta stuff!
    pass


def main():
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        if menu.IS_MENU:
            menu.draw(pygame, WIN, icon, WIDTH, HEIGHT)
        else:
            game_code()
        draw()


if __name__ == "__main__":
    main()

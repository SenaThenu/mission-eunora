import os
import pygame

WIN = pygame.display.set_mode((500, 500))

run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    path = os.path.join("Assets", "MainCharacters", "Mask Dude", "Fall.png")
    img = pygame.image.load(path)
    img_2 = img
    x, y = pygame.mouse.get_pos()
    WIN.fill((0, 0, 0))
    WIN.blit(img, (x, y))
    WIN.blit(img_2, (100, 100))

    mask = pygame.mask.from_surface(img)
    mask_2 = pygame.mask.from_surface(img_2)

    if pygame.sprite.collide_mask(mask, mask_2):
        quit()
    pygame.display.update()

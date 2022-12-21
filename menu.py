from os.path import join

IS_MENU = True


def check_within(button, button_x, button_y, pos):
    within_x = button_x <= pos[0] and pos[0] <= button_x + button.get_width()
    within_y = button_y <= pos[1] and pos[1] <= button_y + button.get_height()
    return within_x, within_y


def draw(pygame, WIN, icon, WIDTH, HEIGHT):
    bg = pygame.image.load(join("Assets", "Menu", "bg.jpg"))
    WIN.blit(bg, (0, 0))

    WIN.blit(icon, (WIDTH//2 - icon.get_width() //
             2, HEIGHT//2 - icon.get_height()//2 - 100))

    start = pygame.image.load(join("Assets", "Buttons", "start.png"))
    start_x, start_y = WIDTH//2 - start.get_width()//2, HEIGHT//2 + 100
    WIN.blit(start, (start_x, start_y))

    global IS_MENU
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            within_x, within_y = check_within(start, start_x, start_y, pos)
            if within_x and within_y:
                IS_MENU = False

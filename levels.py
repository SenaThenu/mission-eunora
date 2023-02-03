import math
import random

min_platform_len = 2
max_platform_len = 5

# TODO: The enemy generator genearates all the enemies at one place...


# def gen_ground(Block, mx_linear, value_range, HEIGHT, side, max_jump):
#     block_list = []
#     used_x = []
#     used_y = []

#     def select_pos():
#         platform_len = random.randint(min_platform_len, max_platform_len)
#         x = random.randrange(0, value_range - (side*max_platform_len), side)
#         while x in used_x:
#             x = random.randrange(
#                 0, value_range - (side*max_platform_len), side)
#         y = random.randrange(max_jump, HEIGHT-(side*3), side)
#         for i in range(platform_len):
#             used_x.append(x + (side * i))
#         return platform_len, x, y

#     for i in range(mx_linear):
#         platform_len, x, y = select_pos()
#         for num in range(platform_len):
#             block_list.append(Block(x + side*num, y, side))

#     return block_list


# def terrain_generator(level, Block, side, max_jump, WIDTH, HEIGHT):
#     terrain = []
#     if level == 1:
#         value_range = WIDTH*3
#         floor = [Block(i*side, HEIGHT-side, side)
#                  for i in range(-5, value_range//side)]
#         mx_linear = 6
#         blocks = gen_ground(Block, mx_linear, value_range,
#                             HEIGHT, side, max_jump)

#         terrain = [*floor, *blocks]

#     return terrain, floor, blocks


def generate_terrain(HEIGHT, Block, min_x, max_x, side):
    terrain = [Block(i*side, HEIGHT-side, side)
               for i in range(min_x//side, max_x//side)]
    return terrain


def generate_wierd_stuff():
    pass


def generate_mount(Block, n_bottom_row, block_side, start_x, HEIGHT):
    block_list = []
    start_y = HEIGHT - (block_side*2)
    for row in range(n_bottom_row):
        begin_x = start_x + (row * block_side // 2)
        start_y = HEIGHT - (block_side*2) - (row * block_side)
        row_blocks = [Block(begin_x + (block_side * multi), start_y, block_side)
                      for multi in range(n_bottom_row - row)]

        for block in row_blocks:
            block_list.append(block)
    return block_list


def obj_generator(Block, Opps, WIDTH, min_x, n_enemies, block_side, n_bottom_row, level, HEIGHT):
    max_x = WIDTH // 2

    enemy_list = {1: ["Rocks"],
                  2: ["Rocks", "AngryPig"],
                  3: ["Rocks", "AngryPig", "Rino"],
                  4: ["Rocks", "AngryPig", "Rino"],
                  5: ["Rocks", "AngryPig", "Rino", "Slime"],
                  6: ["Rocks", "AngryPig", "Rino", "Slime"],
                  7: ["Rocks", "AngryPig", "Rino", "Slime", "Ghost"],
                  8: ["Rocks", "AngryPig", "Rino", "Slime", "Ghost"],
                  9: ["Rocks", "AngryPig", "Rino", "Slime", "Ghost"]}

    enemy_info = {"Rocks": [HEIGHT-block_side-(34*2), 38, 34, "Rocks", "Enemies", 3, 150, 3, False, 4, True],
                  "AngryPig": [HEIGHT-block_side-(30*2), 36, 30, "AngryPig", "Enemies", 3, 250, 3, False, 5, True],
                  "Rino": [HEIGHT-block_side-34*2, 52, 34, "Rino", "Enemies", 3, 300, 3, False, 6, True],
                  "Slime": [HEIGHT-block_side-30*2, 44, 30, "Slime", "Enemies", 3, 400, 3, False, 4, True],
                  "Ghost": [HEIGHT-block_side-31*2, 44, 31, "Ghost", "Enemies", 3, 450, 3, False, 8, True]}                 # Leaving x_position to be added...

    enemy_names = enemy_list.get(level)
    enemies = []

    max_x = WIDTH

    block_add = [max_x]
    mount_blocks = []

    wierd_enumerates = [i for i in range(0, n_enemies, 2)]
    wierd_cors = []
    wierd_area = 500

    for i in range(n_enemies):
        ene_name = random.choice(enemy_names)
        ene_info = enemy_info.get(ene_name)

        enemy_width, enemy_coverage = ene_info[1], ene_info[6]

        enemy_x = max_x + (block_side * n_bottom_row) + \
            enemy_coverage + enemy_width
        enemy_area = enemy_coverage * 2 + (enemy_width*2)

        enemy = Opps(enemy_x, *ene_info)
        enemies.append(enemy)

        max_x += block_side * n_bottom_row + enemy_area

        if i in wierd_enumerates:
            wierd_cors.append((max_x, max_x + wierd_area))
            max_x += wierd_area

        block_add.append(max_x + 50)

    # The Collectibles
    space_for_danger = 750
    max_x += space_for_danger

    danger_start = max_x

    collectible_dic = {1: [(max_x + 200) - 38, HEIGHT-block_side-24*2, 38, 24, "Snail", "Collectibles", 3, 100, 3, False, 2, True],        # Format this to be the arguments for Opps()
                       2: [(max_x + 200) - 44, HEIGHT-block_side-20*2, 44, 20, "Turtle", "Collectibles", 3, 0, 3, True],
                       3: [(max_x + 200) - 40, HEIGHT-block_side-48*2, 40, 48, "FatBird", "Collectibles", 4, 0, 3, True],
                       4: [(max_x + 350) - 30, HEIGHT-block_side-38*2, 30, 38, "Radish", "Collectibles", 4, 350, 3, False, 4, True],
                       5: [(max_x + 500) - 32, HEIGHT-block_side-32*2, 32, 32, "Mushroom", "Collectibles", 5, 500, 3, False, 10, True],
                       6: [(max_x + 750) - 52, HEIGHT-block_side-104*2, 52, 54, "Skull", "Collectibles", 5, 750, 3, False, 15, True],
                       7: [(max_x + 800) - 84, HEIGHT-block_side-38*2, 84, 38, "Chameloen", "Collectibles", 5, 800, 3, False, 8, True],
                       8: [(max_x + 1000) - 64, HEIGHT-block_side-32*2, 64, 32, "Trunk", "Collectibles", 5, 1000, 3, True, 0, True, True, 5, 20],
                       9: [(max_x + 1250) - 44, HEIGHT-block_side-42*2, 44, 42, "Plant", "Collectibles", 5, 1250, 3, True, 0, True, True, 5, 20]}
    collecti = collectible_dic.get(level)

    to_collect = Opps(*collecti)

    max_x += collecti[7] * 2 + (collecti[2]*2) + \
        space_for_danger        # [7] = Coverage
    danger_end = max_x
    block_add.append(max_x)
    max_x += block_side * n_bottom_row

    for to_add in block_add:
        mount = generate_mount(Block, n_bottom_row, block_side, to_add, HEIGHT)
        for block in mount:
            mount_blocks.append(block)

    wierdies = generate_wierd_stuff()

    terrain = generate_terrain(HEIGHT, Block, min_x, max_x, block_side)

    return terrain, enemies, to_collect, mount_blocks, wierdies


def set_level(Block, Opps, WIDTH, HEIGHT):
    block_side = 96

    f = open("level.txt", "r")
    level = int(f.readline())

    min_x = -WIDTH

    level_info = {
        1: 2,
        2: 6,
        3: 7,
        4: 8,
        5: 9,
        6: 10,
        7: 11,
        8: 12,
        9: 13
    }

    n_bottom_row = 6
    n_enemies = level_info.get(level)
    terrain, enemies, to_collect, mount_blocks, wierdies = obj_generator(
        Block, Opps, WIDTH, min_x, n_enemies, block_side, n_bottom_row, level, HEIGHT)

    for i in range(1, math.ceil((HEIGHT)/block_side)):
        terrain.append(
            Block(terrain[0].rect.x, terrain[0].rect.y - (block_side*i), block_side))

    return terrain, mount_blocks, to_collect, enemies, wierdies, level

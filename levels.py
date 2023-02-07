import math
import random


def generate_terrain(HEIGHT, Block, min_x, max_x, side):
    terrain = [Block(i*side, HEIGHT-side, side)
               for i in range(min_x//side, max_x//side)]
    return terrain


# In each (start, end)
def generate_weird_stuff(Weirdies, weird_cors, weird_area, block_side, HEIGHT, Block):
    weird_list = []
    fruit_blocks = []
    weird_info = {
        "Fan": [HEIGHT - block_side - (8*2), 24, 8, "Fan", True, "Off"],
        "Trampoline": [HEIGHT - block_side - (28*2), 28, 28, "Trampoline", True, "Off"],
        "Platform": [HEIGHT - block_side - (96*2), 96, "Platform"],
        "Saw": [HEIGHT - block_side - (38*2), 38, 38, "Saw", True],
        "Fire": [HEIGHT - block_side - (32*2), 16, 32, "Fire", True],
        "Spikes": [HEIGHT - block_side - (16*2), 16, 16, "Spikes", True],
        "Spiked Balls": [HEIGHT - block_side - (28*2), 28, 28, "Spiked Balls", True]
    }
    for cor in weird_cors:
        flyer = random.choice(["Fan", "Trampoline"])
        bottom_danger = random.choice(
            ["Spikes", "Spiked Balls", "Saw", "Fire"])

        start, end = cor

        flyer_info = weird_info.get(flyer)
        flyer_width = flyer_info[1] * 2  # WIDTH :)

        weird_list.append(Weirdies(end-(flyer_width//2), *flyer_info))

        bottom_danger_info = weird_info.get(bottom_danger)
        bottom_danger_width = bottom_danger_info[1]

        for trap_x in range(start, end-flyer_width*2, (bottom_danger_width*2)):
            weird_list.append(Weirdies(trap_x, *bottom_danger_info))

        max_blocks = weird_area // 96 - 1
        n_blocks = random.randint(2, max_blocks)

        block_start_x = start + \
            (((end-flyer_width) - start) - (n_blocks * 96))//2

        for block_num in range(n_blocks):
            block = Block(block_start_x + (block_num * block_side),
                          *weird_info["Platform"])
            weird_list.append(block)
            fruit_blocks.append(block)

    return weird_list, fruit_blocks


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


def obj_generator(Block, Opps, Checkpoint, Weirdies, WIDTH, min_x, n_enemies, block_side, n_bottom_row, level, HEIGHT):
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

    checkpoint_enumearates = [i for i in range(0, n_enemies, 3)]
    checkpoints = []

    weird_enumerates = [i for i in range(0, n_enemies, 2)]
    weird_cors = []
    weird_area = 500

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

        if i in checkpoint_enumearates:
            cp_side = 64
            max_x += cp_side * 2
            checkpoints.append(Checkpoint(
                max_x, HEIGHT-block_side-(cp_side*2), cp_side))
            max_x += cp_side * 4

        if i in weird_enumerates:
            weird_cors.append((max_x, max_x + weird_area))
            max_x += weird_area

        max_x += 50
        block_add.append(max_x)

    # The Collectibles
    max_x += block_side * n_bottom_row
    space_for_danger = 750
    weird_cors.append((max_x, max_x + space_for_danger))
    max_x += space_for_danger

    collectible_dic = {1: [(max_x + 200) - 38, HEIGHT-block_side-24*2, 38, 24, "Snail", "Collectibles", 3, 100, 3, False, 2, True],        # Format this to be the arguments for Opps()
                       2: [(max_x + 200) - 44, HEIGHT-block_side-20*2, 44, 20, "Turtle", "Collectibles", 3, 0, 3, True],
                       3: [(max_x + 200) - 40, HEIGHT-block_side-48*2, 40, 48, "FatBird", "Collectibles", 4, 0, 3, True],
                       4: [(max_x + 350) - 30, HEIGHT-block_side-38*2, 30, 38, "Radish", "Collectibles", 4, 350, 3, False, 4, True],
                       5: [(max_x + 500) - 32, HEIGHT-block_side-32*2, 32, 32, "Mushroom", "Collectibles", 5, 500, 3, False, 10, True],
                       6: [(max_x + 750) - 52, HEIGHT-block_side-54*2, 52, 54, "Skull", "Collectibles", 5, 750, 3, False, 7, True],
                       7: [(max_x + 800) - 84, HEIGHT-block_side-38*2, 84, 38, "Chameleon", "Collectibles", 5, 800, 3, False, 8, True],
                       8: [(max_x + 1000) - 64, HEIGHT-block_side-32*2, 64, 32, "Trunk", "Collectibles", 5, 1000, 3, True, 0, True, True, 5, 20],
                       9: [(max_x + 1250) - 44, HEIGHT-block_side-42*2, 44, 42, "Plant", "Collectibles", 5, 1250, 3, True, 0, True, True, 5, 20]}
    collecti = collectible_dic.get(level)

    to_collect = Opps(*collecti)

    max_x += collecti[7] * 2 + (collecti[2]*2)
    #weird_cors.append((max_x, max_x+space_for_danger))

    max_x += space_for_danger
    block_add.append(max_x)
    max_x += block_side * n_bottom_row

    for to_add in block_add:
        mount = generate_mount(Block, n_bottom_row, block_side, to_add, HEIGHT)
        for block in mount:
            mount_blocks.append(block)

    weirdies, fruit_blocks = generate_weird_stuff(
        Weirdies, weird_cors, weird_area, block_side, HEIGHT, Block)

    terrain = generate_terrain(HEIGHT, Block, min_x, max_x, block_side)

    return terrain, enemies, to_collect, mount_blocks, fruit_blocks, weirdies, checkpoints


def set_level(Block, Opps, Checkpoint, Weirdies, WIDTH, HEIGHT):
    block_side = 96

    f = open("level.txt", "r")
    level = int(f.readline())

    min_x = -WIDTH
    if level <= 9:
        level_info = {                      # 3...
            1: 1,
            2: 1,
            3: 1,
            4: 1,
            5: 1,
            6: 1,
            7: 1,
            8: 1,
            9: 1
        }

        n_bottom_row = 6
        n_enemies = level_info.get(level)
        terrain, enemies, to_collect, mount_blocks, fruit_blocks, weirdies, checkpoints = obj_generator(
            Block, Opps, Checkpoint, Weirdies, WIDTH, min_x, n_enemies, block_side, n_bottom_row, level, HEIGHT)

        for i in range(1, math.ceil((HEIGHT)/block_side)):
            terrain.append(
                Block(terrain[0].rect.x, terrain[0].rect.y - (block_side*i), block_side))

        return terrain, mount_blocks, fruit_blocks, to_collect, enemies, weirdies, checkpoints, level
    else:
        return None, None, None, None, None, None, None, 10

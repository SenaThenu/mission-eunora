import math
import random

max_platform_len = 7
types = ["mountain", "linear", "straight"]


def choose_format(n_flying, max_jump, value_range, side):
    # 0 = starting x_pos, 1 = starting y_pos, 2 = n_platform, 3 = type
    type_list = []
    used_x = []
    used_y = []
    for i in range(n_flying):
        # To make it harder 10 pixels are added to the max_jump
        x = random.randint(0, value_range)
        while x in used_x:
            x = random.randint(0, value_range)
        y = random.randint(0, (max_jump+10))
        while y in used_y:
            y = random.randint(0, (max_jump+10))
        plat_len = random.randint(0, max_platform_len)
        type_list.append([x, y, plat_len, random.choice(type_list)])
        for x_num in range(x, x+(side*plat_len)):
            used_x.append(x_num)
        for y_num in range(y, y+(side*plat_len)):
            used_y.append(y_num)
    return type_list


def terrain_generator(level):
    if level == 1:
        n_flying = 6
        type_list = choose_format(n_flying)


def set_level(Block, WIDTH, HEIGHT, jump_vel, gravity):
    block_side = 96
    max_jump = HEIGHT - (jump_vel/2 * jump_vel/gravity + block_side)

    f = open("level.txt", "r")
    level = int(f.readline())

    if level == 1:
        value_range = WIDTH*3
        floor = [Block(i*block_side, HEIGHT-block_side, block_side)
                 for i in range(-5, value_range//block_side)]
        floor.append(Block(96*5, max_jump, 96))
        floor.append(Block(96*-1, HEIGHT-(96*2), 96))
        floor.append(Block(96*-2, HEIGHT-(96*2), 96))

        for i in range(2, math.ceil((HEIGHT-block_side)//block_side)):
            floor.append(
                Block(floor[0].rect.x, HEIGHT-(block_side*i), block_side))

    return level, floor

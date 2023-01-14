import math
import random

min_platform_len = 2
max_platform_len = 5


def gen_ground(Block, mx_linear, value_range, HEIGHT, side, max_jump):
    block_list = []
    path_to_sky = []
    used_x = []
    used_y = []

    def select_pos():
        platform_len = random.randint(min_platform_len, max_platform_len)
        x = random.randrange(0, value_range - (side*max_platform_len), side)
        while x in used_x:
            x = random.randrange(
                0, value_range - (side*max_platform_len), side)
        y = random.randrange(max_jump, HEIGHT-(side*3), side)
        for i in range(platform_len):
            used_x.append(x + (side * i))
        return platform_len, x, y

    for i in range(mx_linear):
        platform_len, x, y = select_pos()
        for num in range(platform_len):
            block_list.append(Block(x + side*num, y, side))

    return block_list


def terrain_generator(level, Block, side, max_jump, WIDTH, HEIGHT):
    terrain = []
    if level == 1:
        value_range = WIDTH*3
        floor = [Block(i*side, HEIGHT-side, side)
                 for i in range(-5, value_range//side)]
        mx_linear = 6
        blocks = gen_ground(Block, mx_linear, value_range,
                            HEIGHT, side, max_jump)

        terrain = [*floor, *blocks]

    return terrain, floor, blocks


def set_level(Block, WIDTH, HEIGHT, jump_vel, gravity):
    block_side = 96
    max_jump = math.ceil(HEIGHT - (jump_vel/2 * jump_vel/gravity + block_side))
    n_golden_fruit = 3

    f = open("level.txt", "r")
    level = int(f.readline())

    if level == 1:
        terrain, floor, sky_ward = terrain_generator(
            level, Block, block_side, max_jump, WIDTH, HEIGHT)
        n_golden_fruit = 3

    for i in range(1, math.ceil((HEIGHT)/block_side)):
        terrain.append(
            Block(floor[0].rect.x, floor[0].rect.y - (block_side*i), block_side))

    return terrain, n_golden_fruit, sky_ward

# n_flying = 6
#         type_list = choose_format(
#             n_flying, max_jump, value_range, side, HEIGHT)
#         block_list = create_blocks(type_list, Block, side)
#         terrain = [*floor, *block_list]

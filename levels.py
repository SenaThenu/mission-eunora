import math


def set_level(Block, WIDTH, HEIGHT):
    max_jump = HEIGHT - (312 + 96)
    f = open("level.txt", "r")
    level = int(f.readline())
    block_side = 96

    if level == 1:
        floor = [Block(i*block_side, HEIGHT-block_side, block_side)
                 for i in range(-5, WIDTH*5//block_side)]
        floor.append(Block(96*5, max_jump, 96))
        floor.append(Block(96*-1, HEIGHT-(96*2), 96))
        floor.append(Block(96*-2, HEIGHT-(96*2), 96))

        for i in range(2, math.ceil((HEIGHT-block_side)//block_side)):
            floor.append(
                Block(floor[0].rect.x, HEIGHT-(block_side*i), block_side))

    return level, floor

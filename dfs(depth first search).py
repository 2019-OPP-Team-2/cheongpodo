def safe(HEIGHT, WIDTH, DIRECTION):
    global height, width, LEFT, RIGHT, WHITE
    if 0 <= HEIGHT < height and 0 <= WIDTH < width:
        if DIRECTION == LEFT and WIDTH <= width / 2:
            return True
        elif DIRECTION == RIGHT and WIDTH >= width / 2:
            return True
        else:
            return False
    else:
        return False


img = 1
WHITE = 255
LEFT = -1
RIGHT = 1
# img : image file, GRAY color (section = 1)

height, width = (1, 1)
# height, width -> as you know

for color_white in range(height):
    img[color_white][0] = img[color_white][width - 1] = WHITE

# well-defined ( no noise)
left_idx = 0
right_idx = width

# sumation
left_sum = right_sum = 0

# initial
for l_initial in range(width / 2, 0, -1):
    if img[height - 1][l_initial] == WHITE:
        left_idx = l_initial
        left_sum = width / 2 - left_idx
        break
for r_initial in range(width / 2, width):
    if img[height - 1][r_initial] == WHITE:
        right_idx = r_initial
        right_sum = right_idx - width / 2
        break

for this_height in range(height - 2, height * 2 // 3, -1):
    left_sum += (width / 2 - left_idx)
    right_sum += (right_idx - width / 2)
    # 미리 ++시키고, 만약 존재하면 여기에서 -, 만약 찾지 못하면 기존의 WIDTH가 유지된다고 가정

    temp_idx = left_idx
    for this_width in range(temp_idx + 4, temp_idx - 4, -1):
        if safe(HEIGHT=this_height, WIDTH=this_width, DIRECTION=LEFT) and img[this_height][this_width] == WHITE:
            left_sum -= (width / 2 - left_idx)
            left_sum += (width / 2 - this_width)
            left_idx = this_width
            break

    temp_idx = right_idx
    for this_width in range(temp_idx - 4, temp_idx + 4):
        if safe(HEIGHT=this_height, WIDTH=this_width, DIRECTION=LEFT) and img[this_height][this_width] == WHITE:
            right_sum -= (right_idx - width / 2)
            right_sum += (this_width - width / 2)
            right_idx = this_width
            break

# 이제 left_sum, right_sum이 width/2로부터 떨어져 있는 거리들의 합이다. 이를 height // 3으로 나누면 된다.

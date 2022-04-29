import pygame, sys, time
from random import randint

WIDTH, HEIGHT = 1280, 960
BACKGROUND = (128, 128, 128)
OFFSET_Y = 270
OFFSET_X = 72
FIELD_WIDTH, FIELD_HEIGHT = 1136, 644
ROWS, COLUMNS = 20, 20
CELLSIZE = 30.7
if ROWS <= COLUMNS: COLUMNS = int(max(FIELD_WIDTH, FIELD_HEIGHT) / CELLSIZE)
elif COLUMNS <= ROWS: ROWS = int(max(FIELD_WIDTH, FIELD_HEIGHT) / CELLSIZE)

BOMBS = 100

BACKGROUND = (120, 120, 120)
GRID = (0, 0, 0)
DISCOVERED = (180, 180, 180)
FLAGGED = (0, 255, 0)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minesweeper")

field_surf = pygame.surface.Surface((WIDTH, HEIGHT))

def load_assets():
    global assets

    bg_im = pygame.image.load("assets/bg.png")
    bg_im = pygame.transform.scale(bg_im, (WIDTH, HEIGHT))

    retry_im = pygame.image.load("assets/icon.png")
    retry_im = pygame.transform.scale(retry_im, (92, 92))
    retry_pushed_im = pygame.image.load("assets/icon_pushed.png")
    retry_pushed_im = pygame.transform.scale(retry_pushed_im, (92, 92))

    numbers_im = [pygame.image.load(f"assets/{i}.png") for i in range(10)]
    numbers_im = [pygame.transform.scale(numbers_im[i], (52, 92)) for i in range(10)]

    flag_im = pygame.image.load("assets/flag.png")
    flag_im = pygame.transform.scale(flag_im, (int(CELLSIZE), int(CELLSIZE)))
    bomb_im = pygame.image.load("assets/bomb.png")
    bomb_im = pygame.transform.scale(bomb_im, (int(CELLSIZE), int(CELLSIZE)))
    full_im = pygame.image.load("assets/full.png")
    full_im = pygame.transform.scale(full_im, (int(CELLSIZE), int(CELLSIZE)))
    empty_im = pygame.image.load("assets/empty.png")

    mines_im = [empty_im] + [pygame.image.load(f"assets/mines_{i}.png") for i in range(1, 9)]
    mines_im = [pygame.transform.scale(i, (int(CELLSIZE), int(CELLSIZE))) for i in mines_im]

    assets = {"bg": bg_im, "retry": retry_im, "retry_pushed": retry_pushed_im, "numbers": numbers_im, "flag": flag_im, "bomb": bomb_im, "full": full_im, "empty": empty_im, "mines": mines_im}

def generate_number_bombs():
    global field_surf, assets
    
    bombs_str = str(BOMBS)
    number_offset = 52
    number_bombs_position = (1038, 86)
    for i, n in enumerate(bombs_str[::-1]):
        field_surf.blit(assets["numbers"][int(n)], (number_bombs_position[0] + ((2-i) * number_offset), number_bombs_position[1]))

def generate_field():
    global field, discovered, assets, field_surf

    field_surf.blit(assets["bg"], (0, 0))

    for y in range(ROWS):
        for x in range(COLUMNS):
            disco_val = discovered[x][y]
            field_val = field[x][y]
            pos = (x * CELLSIZE) + OFFSET_X, (y * CELLSIZE) + OFFSET_Y
            if disco_val == 0:
                field_surf.blit(assets["full"], pos)
            elif disco_val == 1:
                if field_val == -1:
                    field_surf.blit(assets["bomb"], pos)
                else:
                    field_surf.blit(assets["mines"][field_val], pos)
            elif disco_val == -1:
                field_surf.blit(assets["flag"], pos)

    generate_numbers()
    generate_number_bombs()

def generate_numbers():
    global flags, assets, field_surf

    flags_str = str(flags)

    number_offset = 52
    number_flags_position = (86, 86)
    for i, n in enumerate(flags_str[::-1]):
        field_surf.blit(assets["numbers"][int(n)], (number_flags_position[0] + ((2-i) * number_offset), number_flags_position[1]))

def update_screen(retry_held=False):
    global assets, field_surf, screen

    if retry_held: field_surf.blit(assets["retry_pushed"], (594, 86))
    else: field_surf.blit(assets["retry"], (594, 86))

    screen.blit(field_surf, (0, 0))
    pygame.display.flip()

def increment_neighbors(coord: list):
    global field

    neighbors = get_neighbors(coord)
    for n in neighbors:
        if not n[0] < 0 and not n[1] < 0 and not n[0] > COLUMNS - 1 and not n[1] > ROWS - 1:
            if field[n[0]][n[1]] != -1:
                field[n[0]][n[1]] += 1

def get_neighbors(cell):
    x, y = cell[0], cell[1]
    return [[x - 1, y - 1], [x, y - 1], [x + 1, y - 1], [x - 1, y], [x + 1, y], [x - 1, y + 1], [x, y + 1], [x + 1, y + 1]]

def discover(cell):
    global discovered, field

    change = False
    value = discovered[cell[0]][cell[1]]
    if value >= 0:
        if value == 0:
            discovered[cell[0]][cell[1]] = 1
            change = True
        value_field = field[cell[0]][cell[1]]
        if value_field == 0:
            neighbors = get_neighbors(cell)
            for n in neighbors:
                if 0 <= n[0] < COLUMNS and 0 <= n[1] < ROWS:
                    neighbor_val = discovered[n[0]][n[1]]
                    if field[n[0]][n[1]] >= 0 and neighbor_val == 0 and neighbor_val != -1:
                        discover(n)
                        change = True
        elif value_field == -1:
            for y in range(ROWS):
                for x in range(COLUMNS):
                    discovered[x][y] = 1
            generate_field()
            return -1               # lost
    return change                   # fine

def flag(cell):
    global flags, discovered, field

    value = discovered[cell[0]][cell[1]]

    if value == 0:
        discovered[cell[0]][cell[1]] = -1
        flags += 1
    elif value == -1:
        if check_win(): return 1
        else:
            discovered[cell[0]][cell[1]] = 0
            flags -= 1
        
    generate_field()
    
def check_win():
    global flags, discovered, field

    if flags == BOMBS:
        for y in range(ROWS):
            for x in range(COLUMNS):
                if field[x][y] == -1 and discovered[x][y] != -1: return False
        return True

def retry():
    global field, discovered, flags

    flags = 0

    field = [[0 for y in range(ROWS)] for x in range(COLUMNS)]                  # 0: nothing, -1: bomb, >0: number of bombs around
    discovered = [[0 for y in range(ROWS)] for x in range(COLUMNS)]             # -1: flag, 0: covered, 1: discovered

    # generate the bombs
    for b in range(BOMBS):
        x = randint(0, COLUMNS - 1)
        y = randint(0, ROWS - 1)
        while field[x][y] == -1:
            x = randint(0, COLUMNS - 1)
            y = randint(0, ROWS - 1)

        field[x][y] = -1
        increment_neighbors([x, y])

    start_x, start_y = randint(0, COLUMNS-1), randint(0, ROWS-1)
    while field[start_x][start_y] != 0:
        start_x, start_y = randint(0, COLUMNS-1), randint(0, ROWS-1)
    discovered[start_x][start_y] = 1

    generate_field()

def check_inputs():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button = pygame.mouse.get_pressed(num_buttons=3)
    if OFFSET_Y < mouse_y < HEIGHT - 76 and OFFSET_X < mouse_x < WIDTH - OFFSET_X:
        mouse_x, mouse_y = int((mouse_x - OFFSET_X) / CELLSIZE), int((mouse_y - OFFSET_Y) / CELLSIZE)
        if button[0]:
            change = discover((mouse_x, mouse_y))            # -1: lost, True or False = change
            if change != False:
                generate_field()
        elif button[2]:
            return flag((mouse_x, mouse_y))                 # 1: win
    elif 594 <= mouse_x <= 686 and 86 <= mouse_y <= 178:
        retry()
        return 2                                            # 2: retry button is held down

if __name__ == "__main__":
    load_assets()
    field_surf.fill(BACKGROUND)
    retry()

    retry_held = False
    playing = True

    update_screen()
    while playing:
        start = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                answer = check_inputs()
                if answer == 1:
                    for y in range(ROWS):
                        for x in range(COLUMNS):
                            if field[x][y] != -1: discovered[x][y] = 1
                elif answer == 2:
                    retry_held = True
                if answer != None: generate_field()
            if event.type == pygame.MOUSEBUTTONUP:
                retry_held = False

        update_screen(retry_held)
        end = time.time()
        fps = int(1 / (end - start))
        print(f"{fps}fps\n")
    
    pygame.quit()
    sys.exit()
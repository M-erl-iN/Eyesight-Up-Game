"""Eyesight Up Game v.1"""
import time
import pygame
from random import randrange, choice, sample
from PIL import Image, ImageDraw, ImageFont
import csv
from contextlib import suppress


class Figure(pygame.sprite.Sprite):
    def __init__(self, image, width=None, height=None):
        if width is None:
            width = (WIDTH_U, WIDTH_D)
        if height is None:
            height = (HEIGHT_U, HEIGHT_D)
        pygame.sprite.Sprite.__init__(self)
        image.set_colorkey((0, 0, 0, 0))
        self.image_orig = image
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = randrange(width[0], width[1] - self.rect.width)
        self.rect.y = randrange(height[0], height[1] - self.rect.height)
        self.board_sizes = (width, height)
        self.speedy = rand_speed()
        self.speedx = rand_speed()
        self.speeds_for_true_rotate = (abs(self.speedx), abs(self.speedy))
        self.became_prime = 0

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top < self.board_sizes[1][0]:
            self.speedy = self.speeds_for_true_rotate[1]
        elif self.rect.bottom > self.board_sizes[1][1]:
            self.speedy = -self.speeds_for_true_rotate[1]
        if self.rect.left < self.board_sizes[0][0]:
            self.speedx = self.speeds_for_true_rotate[0]
        elif self.rect.right > self.board_sizes[0][1]:
            self.speedx = -self.speeds_for_true_rotate[0]


class AnimatedFigure(Figure):
    def __init__(self, image, width=0, height=0):
        if width == 0:
            width = (WIDTH_U, WIDTH_D)
        if height == 0:
            height = (HEIGHT_U + 50, HEIGHT_D - 50)
        Figure.__init__(self, image, width, height)
        self.rot = 0
        self.rot_speed = rand_speed()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rotate()
        Figure.update(self)

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 25:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class SplitAnimatedFigure(AnimatedFigure):
    def __init__(self, image, spl_img, lep_count, dif, color1, color2):
        super(SplitAnimatedFigure, self).__init__(image)
        self.split_obj_list = [AnimatedFigure(spl_img) for _ in range(lep_count)]
        self.colors = (color1, color2)
        if dif > medium:
            self.dif = 1
        else:
            self.dif = 2

    def split_(self):
        if self.dif >= medium:
            a, b = 200, 500
        else:
            a, b = 400, 1000
        if randrange(0, randrange(a, b)) == 0:
            return 1
        else:
            return 0

    def update(self):
        super(SplitAnimatedFigure, self).update()
        self.split_()

    def spliting(self):
        for i in self.split_obj_list:
            i.rect.x, i.rect.y = self.rect.x, self.rect.y
            i.speedx = rand_speed()
            i.speedy = rand_speed()
            i.became_prime = self.became_prime
        spl_obj = self.split_obj_list
        self.kill()
        for i in spl_obj:
            gamerun_sprites.add(i)

    def vsp(self, i):
        x, y = self.rect.x + (self.rect.width / 2), self.rect.y + (self.rect.height / 2)
        pygame.draw.circle(screen, self.colors[0], (x, y), i // 2 + 20)
        pygame.draw.circle(screen, self.colors[1], (x, y), i // 2 + 20, 5)


class Button(pygame.sprite.Sprite):
    def __init__(self, shablon_image, pos, bttext, btname, alpha, func, sizefont=54, x=30, tr=1, sz=30):
        a = 'img' + put
        image0 = a + '/buttons/' + shablon_image
        image = a + '/buttons/' + btname
        draw_text(image0, bttext, sizefont, image, x, sz)
        pygame.sprite.Sprite.__init__(self)
        d = pygame.image.load(image).convert_alpha()
        self.image_orig = d
        self.alpha = alpha
        self.func = func
        size = self.image_orig.get_rect()
        self.coords = (*pos, pos[0] + size[2], pos[1] + size[3])
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.tr = tr

    def target(self, i=2):
        self.image.set_alpha(self.alpha + (255 - self.alpha) // 3 * (3 - i))
        if self.tr:
            self.rect[0] = self.coords[0] + i * 2
            self.rect[1] = self.coords[1] + i * 2

    def clicked(self):
        click_sound.play()
        self.func()


class ButtonMusicControl(Button):
    def __init__(self, pos, image, alpha, func, tr=1):
        pygame.sprite.Sprite.__init__(self)
        d = pygame.image.load(image).convert_alpha()
        self.image_orig = d
        self.alpha = alpha
        self.func = func
        size = self.image_orig.get_rect()
        self.coords = (*pos, pos[0] + size[2], pos[1] + size[3])
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.tr = tr


class InputBox:
    def __init__(self, x, y, w, h, parameter, doz='0123456789', doz_len=2):
        self.doz = doz
        self.doz_len = doz_len
        self.rect = pygame.Rect(x, y, w, h)
        self.rect2 = self.rect.copy()
        self.rect2[1] += 7
        self.color = COLOR_INACTIVE
        self.parameter = FONT2.render(parameter, True, COLOR_ACTIVE)
        self.par_x = self.parameter.get_size()[0] + 24
        self.rect2[0] += self.par_x
        self.text = ''
        self.active = False
        self.txt_surface = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect2.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < self.doz_len:
                        if event.unicode == '=':
                            event.unicode = '+'
                        if event.unicode in self.doz:
                            self.text += event.unicode
                self.txt_surface = FONT2.render(self.text, True, self.color)

    def update(self):
        self.txt_surface = FONT2.render(self.text, True, self.color)
        width = max(45, self.txt_surface.get_width() + 5)
        self.rect2.w = width
        self.rect.w = width

    def draw(self, ekran):
        ekran.blit(self.parameter, (self.rect.x + 5, self.rect.y + 5))
        ekran.blit(self.txt_surface, (self.rect.x + 5 + self.par_x, self.rect.y + 5))
        pygame.draw.rect(ekran, self.color, self.rect2, 2)


def draw_text(image, text, size, filename, x, sz):
    """накладывает text с размером шрифта size
     на изображение кнопки и сохраняет как filename"""
    if len(text) == 1:
        w = sz
    else:
        w = 5
    font = ImageFont.truetype("pixel_font.ttf", size, encoding="unic")
    canvas = Image.open(image)

    draw = ImageDraw.Draw(canvas)
    for i in range(len(text)):
        draw.text((x, w + i * 45), text[i], 'white', font)
    canvas.save(filename, "PNG")


def rand_speed():
    return help_for_set_speed(-global_speed, global_speed + 1) * global_speed_koef


def help_for_set_speed(qstart, b):
    a = randrange(qstart, b)
    while not a:
        a = randrange(qstart, b)
    return a


def set_speed_for_decoration_object(obj):
    speeds = [help_for_set_speed(-2, 3) for _ in range(2)]
    obj.speedx, obj.speedy = speeds
    obj.speeds_for_true_rotate = (abs(speeds[0]), abs(speeds[1]))
    return obj


def event_test_exit(event):
    if event.type == pygame.QUIT:
        set_w_h_butt(1008, 132)
        return False
    if event.type == pygame.MOUSEBUTTONDOWN:
        if in_coords(exit_buttonQ.coords, *event.pos):
            click_sound.play()
            set_w_h_butt(1008, 132)
            return False
    if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
        if in_coords(exit_buttonQ.coords, *event.pos):
            exit_buttonQ.target()
    if event.type == pygame.MOUSEMOTION:
        if in_coords(exit_buttonQ.coords, *event.pos):
            exit_buttonQ.target()
        else:
            exit_buttonQ.target(0)
    return True


def in_coords(rect, x, y):
    if rect[0] < x < rect[2] and rect[1] < y < rect[3]:
        return 1
    return 0


def main_menu():
    global back, back_rect, exit_buttonQ, button_exit, back1, split_sprites1_list, split_sprites2_list,\
        rotating_sprites, dont_rotated_sprites, decorations, style
    set_style(style)
    split_sprites2_list = []
    split_sprites1_list = []
    rotating_sprites = []
    dont_rotated_sprites = []
    back = pygame.image.load(bg_dir + "g3.png").convert_alpha()
    back_rect = back.get_rect()
    exit_buttonQ = Button('BT_E.png', (1008, 132), [''], 'BT_TEST.png', 161, lambda x: x, tr=0)
    button_exit = pygame.sprite.Group()
    button_exit.add(exit_buttonQ)
    back1 = pygame.image.load(bg_dir + "g_a.png").convert_alpha()

    """Настройка всего необходимого"""
    for i in dont_rotated_images:
        dont_rotated_sprites.append(pygame.image.load(fg_dir + i).convert_alpha())

    for img in rotating_images:
        rotating_sprites.append(pygame.image.load(fg_dir + img).convert_alpha())

    for i in range(0, len(split_double_sprites), 2):
        split_sprites1_list.append((pygame.image.load(fg_dir + split_double_sprites[i]).convert_alpha(),
                                    sprites_to_colors[split_double_sprites[i]]))
        split_sprites2_list.append(pygame.image.load(fg_dir + split_double_sprites[i + 1]).convert_alpha())
    fon_sound.play()
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    d = 'BS.png'
    buttons_spr = pygame.sprite.Group()
    button1 = Button(d, (570, 132), ['     играть'], 'BT_TEST.png', alpha,
                     lambda: game())
    button2 = Button(d, (570, 132 + 140 * 1), ['    уровень'], 'BT_TEST.png',
                     alpha, lambda: level_settings())
    button3 = Button(d, (570, 132 + 140 * 2), ['   обучение'], 'BT_TEST.png', alpha, lambda: training())
    button4 = Button(d, (570, 132 + 140 * 3), ['  настройки'], 'BT_TEST.png', alpha, lambda: settings())
    mainbuttons = [button1, button2, button3, button4]
    for button in mainbuttons:
        buttons_spr.add(button)
    while running:
        tick.tick(60)
        for event in pygame.event.get():
            running = event_test_exit(event)
            if not running:
                global main_run
                main_run = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in mainbuttons:
                    if in_coords(button.coords, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in mainbuttons:
                    if in_coords(button.coords, *event.pos):
                        button.target()
            if event.type == pygame.MOUSEMOTION:
                for button in mainbuttons:
                    if in_coords(button.coords, *event.pos):
                        button.target()
                    else:
                        button.target(0)
        buttons_spr.update()
        button_exit.update()
        decorations.update()
        fon_sound.play()
        screen.blit(back, back_rect)
        decorations.draw(screen)
        buttons_spr.draw(screen)
        button_exit.draw(screen)
        pygame.display.flip()
    pygame.quit()


def start_game(list__):
    global restart
    list_ = list__.copy()
    spr_start = pygame.sprite.Group()
    im = pygame.image.load(fg_dir + 'prime_image_Y.png').convert_alpha()
    im.set_colorkey(BLACK)
    for i in list_:
        i.image = im
        spr_start.add(i)
    timer_loc = time.time()
    run = True
    while time.time() - timer_loc < 2.0 and run:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False
                    restart = True
                    break
            run = event_test_exit(event)
            if not run:
                return False
        screen.blit(back, back_rect)
        button_exit.draw(screen)
        gamerun_sprites.draw(screen)
        spr_start.draw(screen)
        errors_col_sprs.draw(screen)
        pygame.display.flip()
    spr_start.clear(screen, back)
    for i in list_:
        i.image = i.image_orig
        i.became_prime = 1
    return True


def finish_game(false):
    global restart
    im = pygame.image.load(fg_dir + 'prime_image_Y.png').convert_alpha()
    im.set_colorkey(BLACK)
    im_size = im.get_size()
    false += 1
    true = len(list(filter(lambda object_x: object_x.became_prime, list(gamerun_sprites))))
    errors_energy = list(errors_col_sprs)
    run = True
    true_clicks = 0
    false_clicks = 0
    while run:
        with suppress(Exception):
            screen.fill(BLACK)
            screen.blit(back, back_rect)
            for event in pygame.event.get():
                run = event_test_exit(event)
                if not run:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        run = False
                        restart = True
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for i in list(gamerun_sprites):
                        rect = i.rect.copy()
                        rect[2] += rect[0]
                        rect[3] += rect[1]
                        if in_coords(rect, x, y):
                            if i.became_prime:
                                true_clicks += 1
                                true_sound.play()
                                i.image = im
                                i.image_orig = im
                                i.rect.size = im_size
                            else:
                                false_clicks += 1
                                false_sound.play()
                                errors_energy[-1].kill()
                                errors_energy = errors_energy[:-1]
                                i.kill()
                            break
            if false_clicks == false:
                game_sound.stop()
                lose_sound.play()
                break
            elif true_clicks == true:
                gamerun_sprites.draw(screen)
                for i in list(gamerun_sprites):
                    pygame.draw.rect(screen, GREEN, i.rect, 2)
                pygame.display.flip()
                time.sleep(0.25)
                game_sound.stop()
                win_sound.play()
                break
        for i in list(gamerun_sprites):
            pygame.draw.rect(screen, GREEN, i.rect, 2)
        button_exit.draw(screen)
        gamerun_sprites.draw(screen)
        errors_col_sprs.draw(screen)
        pygame.display.flip()


def func1():
    screen.fill(BLACK)


def func2():
    global flicker_mode_timer
    t = time.time()
    if t - flicker_mode_timer > 0.05:
        flicker_mode_timer = t
        screen.fill((200, 200, 200))
        pygame.display.flip()
        time.sleep(0.02)


def game():
    global gamerun_sprites, animated_spr_list, split_sprites1_list, split_sprites2_list, errors_col_sprs,\
        game_sound, global_level, global_speed_koef, flicker_mode, volume, global_timer, global_speed
    gamerun_sprites, animated_spr_list = pygame.sprite.Group(), []
    errors_col_sprs = pygame.sprite.Group()
    difficulty, dont_rot_col, rot_col, spl_rot_col, prime_col, scale, global_timer,\
        global_speed, global_speed_koef, w, h = global_level
    set_width_and_height(w, h)
    set_w_h_butt(WIDTH_D - 6, HEIGHT_U)
    error_image = pygame.image.load(fg_dir + sc_im).convert_alpha()
    scalefor = scale
    scalej = scalefor // 20 + 1
    for j in range(scalej):
        if scalefor > 20:
            scalei = 20
        else:
            scalei = scale % 20
            if scalefor % 20 == 0 and scalefor != 0:
                scalei = 20
        for i in range(scalei):
            d = pygame.sprite.Sprite()
            d.image = error_image
            d.rect = [WIDTH_D + 10 + j * 30, HEIGHT_U + 55 + 30 * i, 25, 25]
            errors_col_sprs.add(d)
        scalefor -= scalei
    game_finished = False

    """создание не разбивающихся не вращающихся фигур"""
    for i in range(dont_rot_col):
        d = randrange(0, len(dont_rotated_sprites))
        c = Figure(dont_rotated_sprites[d])
        gamerun_sprites.add(c)

    """создание разбивающихся вращающихся фигур"""
    for i in range(spl_rot_col):
        d = randrange(0, len(split_sprites1_list))
        a = split_sprites2_list[d]
        c = SplitAnimatedFigure(split_sprites1_list[d][0], a, 1 + randrange(3), difficulty, *split_sprites1_list[d][1])
        gamerun_sprites.add(c)
        animated_spr_list.append(c)

    """создание неразбивающихся вращающихся фигур"""
    for i in range(rot_col):
        if randrange(0, 250) == 0:
            c = AnimatedFigure(pygame.image.load(fg_dir + 'FT_SPECIAL.png').convert_alpha())
        else:
            d = randrange(0, len(rotating_images))
            c = AnimatedFigure(rotating_sprites[d])
        gamerun_sprites.add(c)

    fon_sound.stop()
    game_sound = pygame.mixer.Sound(choice(game_sound_list))
    game_sound.set_volume(volume)
    game_sound.play()
    if flicker_mode:
        func = func2
    else:
        func = func1
    a1 = sample(list(gamerun_sprites), prime_col)
    """цикл игры"""
    starting = start_game(a1)
    sprts = {}
    running = True
    timer = time.time()
    global flicker_mode_timer
    flicker_mode_timer = time.time()
    global restart
    fps1 = 10
    if starting:
        while running:
            clock.tick(fps1)
            for event in pygame.event.get():
                running = event_test_exit(event)
                if not running:
                    gamerun_sprites, animated_spr_list = pygame.sprite.Group(), []
                    errors_col_sprs = pygame.sprite.Group()
                    game_sound.stop()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running = False
                        restart = True
                        break
            if time.time() - timer < global_timer:
                if fps1 < FPS:
                    fps1 += 2
                gamerun_sprites.update()
                func()
                screen.blit(back, back_rect)
                for i in list(gamerun_sprites):
                    pygame.draw.rect(screen, GREEN, i.rect, 2)
                gamerun_sprites.draw(screen)
                errors_col_sprs.draw(screen)
                for i in range(len(animated_spr_list)):
                    if animated_spr_list[i].split_():
                        sprts[animated_spr_list[i]] = 0
                sprts1 = sprts.copy()
                for i in sprts1.keys():
                    if sprts[i] > 40:
                        if difficulty > normal:
                            a = randrange(3)
                            if a:
                                i.spliting()
                                del animated_spr_list[animated_spr_list.index(i)]
                        else:
                            i.spliting()
                            del animated_spr_list[animated_spr_list.index(i)]
                        del sprts[i]
                    else:
                        i.vsp(sprts[i])
                        sprts[i] += 1
                button_exit.update()
                button_exit.draw(screen)
                pygame.display.flip()
            elif not game_finished:
                finish_game(scale)
                break
        if restart:
            game_sound.stop()
            restart = False
            game()
    game_sound.stop()
    set_w_h_butt(1008, 132)
    fon_sound.play()


def training():
    global backslide
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    buttons_spr = pygame.sprite.Group()
    backslide = pygame.image.load("img/slides/sl1.png").convert_alpha()
    button1 = Button('BT_E.png', (2, 2), [''], 'BT_E.png', alpha,
                     lambda: slide_show())
    image = pygame.image.load('img/BT_SLIDES.png').convert_alpha()
    image.set_colorkey(BLACK)
    button1.image_orig = image
    button1.image = image
    buttons_spr.add(button1)
    while running:
        tick.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_coords(button1.coords, *event.pos):
                    button1.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                if in_coords(button1.coords, *event.pos):
                    button1.target()
            if event.type == pygame.MOUSEMOTION:
                if in_coords(button1.coords, *event.pos):
                    button1.target()
                else:
                    button1.target(0)
        buttons_spr.update()
        screen.blit(backslide, back_rectslide)
        buttons_spr.draw(screen)
        pygame.display.flip()


def slide_show():
    global back_ind, backslide
    if back_ind == 0:
        backslide = pygame.image.load("img/slides/sl2.png").convert_alpha()
        back_ind += 1
    elif back_ind == 1:
        backslide = pygame.image.load("img/slides/sl3.png").convert_alpha()
        back_ind += 1
    elif back_ind == 2:
        backslide = pygame.image.load("img/slides/sl4.png").convert_alpha()
        back_ind += 1
    elif back_ind == 3:
        global global_speed, global_speed_koef, global_level
        global_speed = 2
        global_speed_koef = 2
        gl1 = global_level
        global_level = (1, 2, 2, 0, 1, 40, 10, 2, 2, 480, 600)
        game()
        global_level = gl1
        back_ind = 0
        raise ZeroDivisionError


def set_level(level_for_set, boxes):
    global global_level
    global_level = level_for_set
    boxes[0].text = '-' if global_level[0] < medium else '+'
    for i in range(1, len(boxes)):
        boxes[i].text = str(global_level[i])


def get_player_level(boxes):
    global player_level, global_level
    global_level = player_level
    boxes[0].text = '-' if player_level[0] < medium else '+'
    for i in range(1, len(boxes)):
        boxes[i].text = str(player_level[i])


def set_player_level(boxes):
    global player_level
    player_level[0] = normal if boxes[0].text == '-' else hard
    for i in range(1, len(player_level)):
        player_level[i] = int(boxes[i].text)
    set_level(player_level, boxes)


def set_flicker_mode():
    global flicker_mode
    flicker_mode = (flicker_mode + 1) % 2


def level_settings():
    global decorations
    input_box1 = InputBox(100, 100, 45, 24, 'шары')
    input_box2 = InputBox(100, 150, 45, 24, 'анифиры')
    input_box3 = InputBox(100, 200, 45, 24, 'взрывные анифиры')
    input_box4 = InputBox(100, 250, 45, 24, 'ложные взрывы(+/-)', doz='-+', doz_len=1)
    input_box5 = InputBox(100, 300, 45, 24, 'цели')
    input_box6 = InputBox(100, 350, 45, 24, 'заряды')
    input_box7 = InputBox(600, 100, 45, 24, 'время раунда', doz_len=3)
    input_box8 = InputBox(600, 150, 45, 24, 'скорость', doz_len=3)
    input_box9 = InputBox(600, 200, 45, 24, 'коэффициент скорости', doz_len=3)
    input_box10 = InputBox(600, 250, 45, 24, 'ширина поля(max:1488)', doz_len=5)
    input_box11 = InputBox(600, 300, 45, 24, 'высота поля(max:824)', doz_len=4)
    input_boxes = [input_box4, input_box1, input_box2, input_box3, input_box5, input_box6,
                   input_box7, input_box8, input_box9, input_box10, input_box11]
    button = Button('BSe.png', (570, 132 + 140 * 3), ['сохранить'], 'BT_TEST.png', 161,
                    lambda: set_player_level(input_boxes), sz=17, sizefont=44)
    button1 = Button('BSe.png', (20, 760), ['     easy'], 'BT_TEST.png', 161,
                     lambda: set_level(easy_level, input_boxes), sz=17, sizefont=44)
    button2 = Button('BSe.png', (320, 760), ['  normal'], 'BT_TEST.png', 161,
                     lambda: set_level(normal_level, input_boxes), sz=17, sizefont=44)
    button3 = Button('BSe.png', (620, 760), ['  medium'], 'BT_TEST.png', 161,
                     lambda: set_level(medium_level, input_boxes), sz=17, sizefont=44)
    button4 = Button('BSe.png', (920, 760), ['     hard'], 'BT_TEST.png', 161,
                     lambda: set_level(hard_level, input_boxes), sz=17, sizefont=44)
    button5 = Button('BSe.png', (1220, 760), ['   demon'], 'BT_TEST.png', 161,
                     lambda: set_level(demon_level, input_boxes), sz=17, sizefont=44)
    button6 = Button('BSe.png', (1220, 650), ['   player'], 'BT_TEST.png', 161,
                     lambda: set_level(player_level, input_boxes), sz=17, sizefont=44)
    button7 = Button('BSe.png', (920, 650), [' flicker!?'], 'BT_TEST.png', 161,
                     lambda: set_flicker_mode(), sz=17, sizefont=44)
    buttons_spr = pygame.sprite.Group()
    setting_buttons = [button, button1, button2, button3, button4, button5, button6, button7]
    for button in setting_buttons:
        buttons_spr.add(button)
    done = True
    while done:
        screen.blit(back, back_rect)
        for event in pygame.event.get():
            done = event_test_exit(event)
            for box in input_boxes:
                box.handle_event(event)
            if not done:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in setting_buttons:
                    if in_coords(button.coords, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in setting_buttons:
                    if in_coords(button.coords, *event.pos):
                        button.target()
            if event.type == pygame.MOUSEMOTION:
                for button in setting_buttons:
                    if in_coords(button.coords, *event.pos):
                        button.target()
                    else:
                        button.target(0)
        with suppress(Exception):
            if int(input_box10.text) > 1488:
                input_box10.text = '1488'
            if int(input_box11.text) > 824:
                input_box11.text = '824'
        buttons_spr.update()
        button_exit.update()
        decorations.update()
        decorations.draw(screen)
        buttons_spr.draw(screen)
        button_exit.draw(screen)
        for box in input_boxes:
            box.update()
        for box in input_boxes:
            box.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def set_width_and_height(w, h):
    w1, h1 = 743, 432
    global WIDTH_D, HEIGHT_D, WIDTH_U, HEIGHT_U, exit_buttonQ
    WIDTH_D, HEIGHT_D = w1 + w // 2, h1 + h // 2
    WIDTH_U, HEIGHT_U = w1 - w // 2, h1 - h // 2


def set_w_h_butt(w, h):
    exit_buttonQ.rect[0] = w
    exit_buttonQ.rect[1] = h
    exit_buttonQ.coords = [w, h, w + 47, h + 47]


def import_style():
    global style
    style = (style + 1) % 2
    set_style(style)
    raise ZeroDivisionError


def set_volume():
    global sounds, volume
    for i in sounds:
        i.set_volume(volume)


def help_volume():
    global music_volume_sprites, volume, music_image
    music_volume_sprites = pygame.sprite.Group()
    volume = round(volume, 1)
    for i in range(int(volume * 10)):
        d = pygame.sprite.Sprite()
        d.image = music_image
        d.rect = [475 + 60 * i, 80, 43, 25]
        music_volume_sprites.add(d)


def plus_volume():
    global volume
    if volume < 1.0:
        volume = volume + 0.1
        set_volume()
        help_volume()


def minus_volume():
    global volume
    if volume > 0.0:
        volume = volume - 0.1
        set_volume()
        help_volume()


def settings():
    global music_volume_sprites, decorations
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    d = 'BS.png'
    buttons_spr = pygame.sprite.Group()
    button1 = Button(d, (570, 132), ['      стиль'], 'BT_TEST.png', alpha,
                     lambda: import_style())
    button3 = ButtonMusicControl((460, 297), 'img/MusicControl/music_control_minus.png', alpha,
                                 lambda: minus_volume())
    button4 = ButtonMusicControl((1010, 297), 'img/MusicControl/music_control_plus.png', alpha,
                                 lambda: plus_volume())
    button2 = pygame.sprite.Sprite()
    draw_text('img' + put + '/buttons/BS.png', ['      звук'], 54, 'img' + put + '/buttons/BT_TEST.png', 30, 30)
    button2.image = pygame.image.load('img' + put + '/buttons/BT_TEST.png').convert_alpha()
    button2.rect = button2.image.get_rect()
    button2.rect.x, button2.rect.y = 570, 272
    button2_ = pygame.sprite.Group(button2)
    main_settings_buttons = [button1, button3, button4]
    for button in main_settings_buttons:
        buttons_spr.add(button)
    while running:
        tick.tick(60)
        for event in pygame.event.get():
            running = event_test_exit(event)
            if not running:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in main_settings_buttons:
                    if in_coords(button.coords, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in main_settings_buttons:
                    if in_coords(button.coords, *event.pos):
                        button.target()
            if event.type == pygame.MOUSEMOTION:
                for button in main_settings_buttons:
                    if in_coords(button.coords, *event.pos):
                        button.target()
                    else:
                        button.target(0)
        buttons_spr.update()
        button_exit.update()
        decorations.update()
        fon_sound.play()
        screen.blit(back, back_rect)
        decorations.draw(screen)
        music_volume_sprites.draw(screen)
        button2_.draw(screen)
        buttons_spr.draw(screen)
        button_exit.draw(screen)
        pygame.display.flip()
    pygame.quit()


def set_style(style_for_set):
    global bt_dir, bg_dir, fg_dir, put, colors, sprites_to_colors, decorations
    decorations = pygame.sprite.Group()
    if style_for_set:
        bt_dir = 'img/NewYear/buttons/'
        bg_dir = 'img/NewYear/backgrounds/'
        fg_dir = 'img/NewYear/figures/'
        put = '/NewYear'
        colors = (((0, 219, 0), (0, 128, 0)), ((255, 167, 112), (255, 98, 0)))
        sprites_to_colors = {'FT2.png': colors[0], 'FS_2.png': colors[1]}
    else:
        bt_dir = 'img/Standart/buttons/'
        bg_dir = 'img/Standart/backgrounds/'
        fg_dir = 'img/Standart/figures/'
        put = '/Standart'
        colors = ((200, 255, 252), (65, 255, 252))
        sprites_to_colors = {'FT2.png': colors, 'FS_2.png': colors}
    for i in range(2):
        decorations.add(set_speed_for_decoration_object(Figure(pygame.image.load(fg_dir + '/ball2.png').convert_alpha(),
                                                               (15, 1521), (15, 849))))
    animated_figures_names = ['/FS_2_2.png', '/FS_2.png', '/FT4.png', '/prime_image_B.png', '/FT3.png', '/FT2.png']
    for i in range(5):
        for j in range(2):
            decorations.add(set_speed_for_decoration_object(
                AnimatedFigure(pygame.image.load(fg_dir + animated_figures_names[i]).convert_alpha(),
                               (15, 1521), (15, 849))))
    if not randrange(25):
        decorations.add(set_speed_for_decoration_object(AnimatedFigure(
            pygame.image.load(fg_dir + '/FT_SPECIAL.png').convert_alpha(), (15, 1521), (15, 849))))
    energy_image = pygame.image.load(fg_dir + '/score_chunk1.png').convert_alpha()
    for i in range(5):
        decorations.add(set_speed_for_decoration_object(AnimatedFigure(energy_image, (15, 1521), (15, 849))))


volume = 0
level = 0
style = 0
with open('level.csv', encoding="utf8") as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for index, q in enumerate(reader):
        if q[0] == '':
            break
        elif not index:
            level = [int(i) for i in q[1:]]
            style = int(q[0])
        elif index:
            player_level = [int(i) for i in q[:-3]]
            volume = float(q[-3])
            global_speed = int(q[-2])
            global_speed_koef = int(q[-1])
buttons, WIDTH_D, HEIGHT_D, WIDTH_U, HEIGHT_U, FPS, speed, BLACK = [], 0, 0, 0, 0, 60, 6, (0, 0, 0)
GREEN = (0, 255, 0)
speed_koef = 1
rotating_images = ['FT4.png']
sc_im = 'score_chunk1.png'
split_double_sprites = ['FT2.png', 'FT3.png', 'FS_2.png', 'FS_2_2.png']
animated_spr_list, split_sprites1_list, split_sprites2_list, rotating_sprites = [], [], [], []
dont_rotated_images = ['ball2.png']
dont_rotated_sprites = []
gamerun_sprites = pygame.sprite.Group()
bt_dir = 'img/NewYear/buttons/'
bg_dir = 'img/NewYear/backgrounds/'
fg_dir = 'img/NewYear/figures/'
put = '/NewYear'
colors = (((0, 219, 0), (0, 128, 0)), ((255, 167, 112), (255, 98, 0)))
sprites_to_colors = {'FT2.png': colors[0], 'FS_2.png': colors[1]}
pygame.init()
pygame.mixer.init()
click_sound = pygame.mixer.Sound("sounds/click.ogg")
start_sound = pygame.mixer.Sound("sounds/start_game.ogg")
start_sound.set_volume(0.7)
win_sound = pygame.mixer.Sound("sounds/WG.ogg")
lose_sound = pygame.mixer.Sound("sounds/LG.ogg")
false_sound = pygame.mixer.Sound("sounds/FC.ogg")
true_sound = pygame.mixer.Sound("sounds/TC.ogg")
fon_sound = pygame.mixer.Sound("sounds/fon.ogg")
game_sound = pygame.mixer.Sound("sounds/GS2.ogg")
game_sound_list = ("sounds/GS1.ogg", "sounds/GS2.ogg", "sounds/GS3.ogg")
flicker_mode_timer = 0
sounds = (click_sound, start_sound, win_sound, lose_sound, false_sound, true_sound, fon_sound, game_sound)
set_volume()
FONT = pygame.font.Font('pixel_font.ttf', 32)
screen = pygame.display.set_mode((1536, 864))
pygame.display.set_caption("Eyesight Up Game")
pygame.display.set_icon(pygame.image.load('icon/active_exe_icon.png').convert_alpha())
clock = pygame.time.Clock()
set_style(style)
back = pygame.image.load(bg_dir + "g3.png").convert_alpha()
back_rect = back.get_rect()
easy = 1
normal = 2
medium = 3
hard = 4
demon = 5
COLOR_ACTIVE = pygame.Color((255, 255, 255))
COLOR_INACTIVE = pygame.Color((195, 195, 195))
FONT2 = pygame.font.Font('pixel_font.ttf', 24)
global_timer = 0
flicker_mode = 0
easy_level = (1, 3, 3, 0, 2, 1, 10, 2, 2, 480, 600)
normal_level = (2, 3, 2, 2, 2, 2, 15, 2, 2, 700, 720)
medium_level = (3, 3, 3, 3, 3, 2, 20, 2, 2, 700, 720)
hard_level = (4, 3, 2, 5, 3, 3, 25, 3, 3, 1486, 864)
demon_level = (5, 4, 4, 4, 4, 0, 30, 4, 4, 1486, 864)
global_level = level
restart = False
music_image = pygame.image.load('img/MusicControl/music_control_count_image.png').convert_alpha()
exit_buttonQ = ButtonMusicControl((1481, 5), 'img' + put + '/buttons/BT_E.png', 161, lambda x: x)
button_exit = pygame.sprite.Group()
button_exit.add(exit_buttonQ)
errors_col_sprs = pygame.sprite.Group()
decorations = pygame.sprite.Group()
music_volume_sprites = pygame.sprite.Group()
help_volume()
start_sound.play()
back1 = pygame.image.load(bg_dir + "g_a.png").convert_alpha()
backslide = pygame.image.load("img/slides/sl1.png").convert_alpha()
back_rectslide = back.get_rect()
back_ind = 0
main_run = True
for i in range(255, 0, -3):
    backanimated = back1.copy()
    backanimated.fill((i, i, i), special_flags=pygame.BLEND_RGB_ADD)
    screen.fill(BLACK)
    screen.blit(backanimated, back_rect)
    pygame.display.flip()
while main_run:
    with suppress(Exception):
        main_menu()
with open('level.csv', 'w', newline='', encoding='utf8') as csvfile:
    writer = csv.writer(
        csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([style, *global_level])
    writer.writerow([*player_level, volume, global_speed, global_speed_koef])

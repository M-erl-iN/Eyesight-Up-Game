# EyesightUpGame
import csv
import time
from contextlib import suppress
from os import listdir, remove
from random import choice, randrange, sample
from webbrowser import open as open_site

import pygame
from PIL import Image, ImageDraw, ImageFont
from win32api import GetSystemMetrics

from materials.color_information import *


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
        self.speed_x = rand_speed()
        self.speeds_for_true_rotate = (abs(self.speed_x), abs(self.speedy))
        self.became_prime = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speedy
        if self.rect.top < self.board_sizes[1][0]:
            self.speedy = self.speeds_for_true_rotate[1]
        elif self.rect.bottom > self.board_sizes[1][1]:
            self.speedy = -self.speeds_for_true_rotate[1]
        if self.rect.left < self.board_sizes[0][0]:
            self.speed_x = self.speeds_for_true_rotate[0]
        elif self.rect.right > self.board_sizes[0][1]:
            self.speed_x = -self.speeds_for_true_rotate[0]


class AnimatedFigure(Figure):
    def __init__(self, image, width=0, height=0):
        if width == 0:
            width = (WIDTH_U, WIDTH_D)
        if height == 0:
            height = (HEIGHT_U, HEIGHT_D)
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
            a, b = 200, main_but_sizes[9] + 50
        else:
            a, b = 400, 1000
        if randrange(0, randrange(a, b)) == 0:
            return 1
        else:
            return 0

    def update(self):
        super(SplitAnimatedFigure, self).update()
        self.split_()

    def segmentation(self):
        for i in self.split_obj_list:
            i.rect.x, i.rect.y = self.rect.x, self.rect.y
            i.speed_x = rand_speed()
            i.speedy = rand_speed()
            i.became_prime = self.became_prime
        spl_obj = self.split_obj_list
        self.kill()
        for i in spl_obj:
            game_process_sprites.add(i)

    def flash(self, i):
        x, y = self.rect.x + (self.rect.width / 2), self.rect.y + (self.rect.height / 2)
        pygame.draw.circle(screen, self.colors[0], (x, y), i // 2 + 20)
        pygame.draw.circle(screen, self.colors[1], (x, y), i // 2 + 20, 5)


class Button(pygame.sprite.Sprite):
    def __init__(
        self,
        template_image,
        pos,
        button_text,
        button_name,
        alpha,
        func,
        font_size=54,
        x=30,
        tr=1,
        sz=30,
        animate_ind=0,
        animation_delay=0,
    ):
        self.animate_ind = animate_ind
        self.animation_delay = animation_delay
        a = "materials/img/Style/buttons/"
        image0 = a + template_image
        image = a + button_name
        draw_text(image0, button_text, font_size, image, x, sz)
        pygame.sprite.Sprite.__init__(self)
        d = pygame.image.load(image).convert_alpha()
        self.current_animation_step = 1
        self.route = 1
        self.route_animate = 1
        self.route_animate_delay = 1
        self.animation_time = 1 * 6
        self.current_animation_time = 0
        self.image_orig = d
        self.alpha = alpha
        self.func = func
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x += 4
        self.rect.y += 4
        self.rect.width -= 8
        self.rect.height -= 8
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.was_targeted = 0
        self.tr = tr
        self.target_step = 0
        self.stroke_delay = 0
        if self.animation_delay:
            self.update = self.animation_delay_function
        else:
            self.update = self.step_targets

    def target(self, i=2):
        self.image.set_alpha(self.alpha + (255 - self.alpha) // 3 * (3 - i))
        if i == 2 and not self.was_targeted:
            self.was_targeted = 1
        elif i == 0 and self.was_targeted:
            self.was_targeted = 0

    def clicked(self):
        self.func()

    def animation_delay_function(self):
        if self.animate_ind:
            self.animate_ind -= 1
        else:
            self.update = self.update_animate

    def update_animate(self):
        if self.animation_delay:
            self.current_animation_time += 1
            if (
                self.current_animation_time
                >= self.animation_time / animation_steps[self.current_animation_step]
            ):
                if self.current_animation_step == steps_count - 1:
                    self.route = -1
                    self.route_animate_delay = 1
                elif self.current_animation_step == 1 and self.route_animate_delay:
                    self.route = 1
                    self.route_animate *= -1
                    self.route_animate_delay = 0
                self.rect.y += self.route_animate
                self.current_animation_time = 0
                self.current_animation_step += self.route
        else:
            self.animate_ind -= 1
        self.step_targets()

    def step_targets(self):
        if self.stroke_delay:
            self.stroke_delay = 0
            if self.was_targeted:
                if self.target_step < 8:
                    self.target_step += 1
                    self.rect.x += 1
                    self.rect.y += 1
            else:
                if self.target_step > 0:
                    self.target_step -= 1
                    self.rect.x -= 1
                    self.rect.y -= 1
        else:
            self.stroke_delay = 1


class ButtonMusicControl(Button):
    def __init__(self, pos, image, alpha, func, tr=1):
        pygame.sprite.Sprite.__init__(self)
        d = pygame.image.load(image).convert_alpha()
        self.image_orig = d
        self.alpha = alpha
        self.func = func
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.tr = tr
        self.was_targeted = 0

    def update(self):
        pygame.sprite.Sprite.update(self)


class InputBox:
    def __init__(self, x, y, w, h, parameter, doz="0123456789", doz_len=2):
        self.doz = doz
        self.doz_len = doz_len
        self.rect = pygame.Rect(x, y, w, h)
        self.rect2 = self.rect.copy()
        self.rect2[1] += 7
        self.color = COLOR_INACTIVE
        self.parameter = FONT2.render(parameter, True, COLOR_ACTIVE)
        self.par_x = self.parameter.get_size()[0] + main_but_sizes[8]
        self.rect2[0] += self.par_x
        self.text = ""
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
                        if event.unicode == "=":
                            event.unicode = "+"
                        if event.unicode in self.doz:
                            self.text += event.unicode
                self.txt_surface = FONT2.render(self.text, True, self.color)

    def update(self):
        self.txt_surface = FONT2.render(self.text, True, self.color)
        width = max(main_but_sizes[9], self.txt_surface.get_width() + 5)
        self.rect2.w = width
        self.rect.w = width

    def draw(self, canvas):
        canvas.blit(self.parameter, (self.rect.x + 5, self.rect.y + 5))
        canvas.blit(self.txt_surface, (self.rect.x + 5 + self.par_x, self.rect.y + 5))
        pygame.draw.rect(canvas, self.color, self.rect2, 2)


def draw_text(image, text, font_size, filename, x, sz):
    if len(text) == 1:
        w = sz
    else:
        w = 5
    font = ImageFont.truetype("materials/font.ttf", font_size, encoding="unic")
    canvas = Image.open(image)

    draw = ImageDraw.Draw(canvas)
    for i in range(len(text)):
        draw.text((x, w + i * main_but_sizes[9]), text[i], button_color1, font)
    canvas.save(filename, "PNG")


def set_factor_for_img(img_name):
    img = Image.open(img_name)
    x, y = img.size
    if x != size[0] or y != size[1]:
        img_converted = img.resize(ret_sizes(x, y))
        img_converted.save(img_name)


def ret_sizes(x, y):
    return [ret_size_x(x), ret_size_y(y)]


def ret_size_x(x):
    return int(x / coefficients[0])


def ret_size_y(y):
    return int(y / coefficients[1])


def rand_speed():
    return help_for_set_speed(-global_speed, global_speed + 1) * global_speed_factor


def help_for_set_speed(segment_start, segment_end):
    figure_speed = randrange(segment_start, segment_end)
    while not figure_speed:
        figure_speed = randrange(segment_start, segment_end)
    return figure_speed


def set_speed_for_decoration_object(obj):
    speeds = [help_for_set_speed(-2, 3) for _ in range(2)]
    obj.speed_x, obj.speedy = speeds
    obj.speeds_for_true_rotate = (abs(speeds[0]), abs(speeds[1]))
    return obj


def event_test_exit(event):
    if event.type == pygame.QUIT:
        set_w_h_butt(*ex_size_)
        return False
    if event.type == pygame.MOUSEBUTTONDOWN:
        if in_coordinates_rect(exit_buttonQ.rect, *event.pos):
            set_w_h_butt(*ex_size_)
            return False
    if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
        if in_coordinates_rect(exit_buttonQ.rect, *event.pos):
            exit_buttonQ.target()
    if event.type == pygame.MOUSEMOTION:
        if in_coordinates_rect(exit_buttonQ.rect, *event.pos):
            exit_buttonQ.target()
        else:
            exit_buttonQ.target(0)
    return True


def in_coordinates(rect, x, y):
    if rect[0] < x < rect[2] and rect[1] < y < rect[3]:
        return 1
    return 0


def in_coordinates_rect(rect, x, y):
    if rect.x < x < rect.x + rect.width and rect.y < y < rect.y + rect.height:
        return 1
    return 0


def main_menu():
    global back, back_rect, exit_buttonQ, button_exit, back1, split_sprites1_list, split_sprites2_list,\
        rotating_sprites, not_rotated_sprites, decorations
    split_sprites2_list = []
    split_sprites1_list = []
    rotating_sprites = []
    not_rotated_sprites = []
    back = pygame.image.load(bg_dir + "g3.png").convert_alpha()
    back_rect = back.get_rect()
    exit_buttonQ = Button(
        "BT_E.png", ex_size_, [""], "NewButton.png", 161, lambda x: x, tr=0
    )
    button_exit = pygame.sprite.Group()
    button_exit.add(exit_buttonQ)
    back1 = pygame.image.load(bg_dir + "g_a.png").convert_alpha()

    for i in not_rotated_images:
        not_rotated_sprites.append(pygame.image.load(fg_dir + i).convert_alpha())

    for img in rotating_images:
        rotating_sprites.append(pygame.image.load(fg_dir + img).convert_alpha())

    for i in range(0, len(split_double_sprites), 2):
        split_sprites1_list.append(
            (
                pygame.image.load(fg_dir + split_double_sprites[i]).convert_alpha(),
                sprites_to_colors[split_double_sprites[i]],
            )
        )
        split_sprites2_list.append(
            pygame.image.load(fg_dir + split_double_sprites[i + 1]).convert_alpha()
        )
    background_music.play()
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    d = "BS.png"
    buttons_spr = pygame.sprite.Group()
    button1 = Button(
        d,
        (main_but_sizes[0], main_but_sizes[1]),
        ["     играть"],
        "NewButton.png",
        alpha,
        lambda: game(),
        animation_delay=1,
    )
    button2 = Button(
        d,
        (main_but_sizes[0], main_but_sizes[1] + main_but_sizes[2]),
        ["    уровень"],
        "NewButton.png",
        alpha,
        lambda: level_settings(),
        animate_ind=8,
        animation_delay=1,
    )
    button3 = Button(
        d,
        (main_but_sizes[0], main_but_sizes[1] + main_but_sizes[2] * 2),
        ["   обучение"],
        "NewButton.png",
        alpha,
        lambda: training(),
        animate_ind=16,
        animation_delay=1,
    )
    button4 = Button(
        d,
        (main_but_sizes[0], main_but_sizes[1] + main_but_sizes[2] * 3),
        ["  настройки"],
        "NewButton.png",
        alpha,
        lambda: settings(),
        animate_ind=24,
        animation_delay=1,
    )
    main_buttons = [button1, button2, button3, button4]
    for button in main_buttons:
        buttons_spr.add(button)
    while running:
        tick.tick(FPS)
        for event in pygame.event.get():
            running = event_test_exit(event)
            if not running:
                global main_run
                main_run = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in main_buttons:
                    if in_coordinates_rect(button.rect, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in main_buttons:
                    if in_coordinates_rect(button.rect, *event.pos):
                        button.target()
        mouse_pos = pygame.mouse.get_pos()
        for button in main_buttons:
            if in_coordinates_rect(button.rect, *mouse_pos):
                button.target()
            else:
                button.target(0)
        buttons_spr.update()
        button_exit.update()
        decorations.update()
        background_music.play()
        screen.blit(back, back_rect)
        decorations.draw(screen)
        buttons_spr.draw(screen)
        button_exit.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
    pygame.quit()


def start_game(list__):
    global restart
    list_ = list__.copy()
    spr_start = pygame.sprite.Group()
    im = pygame.image.load(fg_dir + "prime_image_Y.png").convert_alpha()
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
        game_process_sprites.draw(screen)
        spr_start.draw(screen)
        errors_col_sprites.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
    spr_start.clear(screen, back)
    for i in list_:
        i.image = i.image_orig
        i.became_prime = 1
    return True


def finish_game(false):
    global restart
    im = pygame.image.load(fg_dir + "prime_image_Y.png").convert_alpha()
    im.set_colorkey(BLACK)
    im_size = im.get_size()
    false += 1
    true = len(
        list(filter(lambda object_x: object_x.became_prime, list(game_process_sprites)))
    )
    errors_energy = list(errors_col_sprites)
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
                    for i in list(game_process_sprites):
                        rect = i.rect.copy()
                        rect[2] += rect[0]
                        rect[3] += rect[1]
                        if in_coordinates(rect, x, y):
                            if i.became_prime:
                                true_clicks += 1
                                correct_choice_sound.play()
                                i.image = im
                                i.image_orig = im
                                i.rect.size = im_size
                            else:
                                false_clicks += 1
                                incorrect_choice_sound.play()
                                errors_energy[-1].kill()
                                errors_energy = errors_energy[:-1]
                                i.kill()
                            break
            if false_clicks == false:
                game_music.stop()
                lose_sound.play()
                break
            elif true_clicks == true:
                game_process_sprites.draw(screen)
                for i in list(game_process_sprites):
                    pygame.draw.rect(screen, RECT_COLOR, i.rect, 2)
                screen.blit(cursor, (pygame.mouse.get_pos()))
                pygame.display.flip()
                time.sleep(0.25)
                game_music.stop()
                win_sound.play()
                break
        for i in list(game_process_sprites):
            pygame.draw.rect(screen, RECT_COLOR, i.rect, 2)
        button_exit.draw(screen)
        game_process_sprites.draw(screen)
        errors_col_sprites.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()


def game():
    global game_process_sprites, animated_spr_list, split_sprites1_list, split_sprites2_list, errors_col_sprites,\
        game_music, global_level, global_speed_factor, volume, global_timer, global_speed
    game_process_sprites, animated_spr_list = pygame.sprite.Group(), []
    errors_col_sprites = pygame.sprite.Group()
    (
        difficulty,
        not_rot_col,
        rot_col,
        spl_rot_col,
        prime_col,
        scale,
        global_timer,
        global_speed,
        global_speed_factor,
        (w),
        h,
    ) = global_level
    set_width_and_height(w, h)
    set_w_h_butt(WIDTH_D - 6, HEIGHT_U - 50)
    error_image = pygame.image.load(fg_dir + sc_im).convert_alpha()
    scale_for_cycle = scale
    scale_j = scale_for_cycle // 20 + 1
    for j in range(scale_j):
        if scale_for_cycle > 20:
            scale_i = 20
        else:
            scale_i = scale % 20
            if scale_for_cycle % 20 == 0 and scale_for_cycle != 0:
                scale_i = 20
        for i in range(scale_i):
            d = pygame.sprite.Sprite()
            d.image = error_image
            d.rect = [WIDTH_D + 10 + j * 30, HEIGHT_U + 55 + 30 * i, 25, 25]
            errors_col_sprites.add(d)
        scale_for_cycle -= scale_i
    game_finished = False

    for i in range(not_rot_col):
        d = randrange(0, len(not_rotated_sprites))
        c = Figure(not_rotated_sprites[d])
        game_process_sprites.add(c)

    for i in range(spl_rot_col):
        d = randrange(0, len(split_sprites1_list))
        a = split_sprites2_list[d]
        c = SplitAnimatedFigure(
            split_sprites1_list[d][0],
            a,
            1 + randrange(3),
            difficulty,
            *split_sprites1_list[d][1],
        )
        game_process_sprites.add(c)
        animated_spr_list.append(c)

    for i in range(rot_col):
        if randrange(0, 250) == 0:
            c = AnimatedFigure(
                pygame.image.load(fg_dir + "FT_SPECIAL.png").convert_alpha()
            )
        else:
            d = randrange(0, len(rotating_images))
            c = AnimatedFigure(rotating_sprites[d])
        game_process_sprites.add(c)

    background_music.stop()
    game_music = pygame.mixer.Sound(choice(game_music_list))
    game_music.set_volume(volume)
    game_music.play()
    a1 = sample(list(game_process_sprites), prime_col)

    starting = start_game(a1)
    sprites = {}
    running = True
    timer = time.time()
    global restart
    fps1 = 10
    if starting:
        while running:
            clock.tick(fps1)
            for event in pygame.event.get():
                running = event_test_exit(event)
                if not running:
                    game_process_sprites, animated_spr_list = pygame.sprite.Group(), []
                    errors_col_sprites = pygame.sprite.Group()
                    game_music.stop()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        running = False
                        restart = True
                        break
            if time.time() - timer < global_timer:
                if fps1 < FPS:
                    fps1 += 2
                game_process_sprites.update()
                screen.blit(back, back_rect)
                for i in list(game_process_sprites):
                    pygame.draw.rect(screen, RECT_COLOR, i.rect, 2)
                game_process_sprites.draw(screen)
                errors_col_sprites.draw(screen)
                for i in range(len(animated_spr_list)):
                    if animated_spr_list[i].split_():
                        sprites[animated_spr_list[i]] = 0
                sprites_copy = sprites.copy()
                for i in sprites_copy.keys():
                    if sprites[i] > 40:
                        if difficulty > normal:
                            a = randrange(3)
                            if a:
                                i.segmentation()
                                del animated_spr_list[animated_spr_list.index(i)]
                        else:
                            i.segmentation()
                            del animated_spr_list[animated_spr_list.index(i)]
                        del sprites[i]
                    else:
                        i.flash(sprites[i])
                        sprites[i] += 1
                button_exit.update()
                button_exit.draw(screen)
                screen.blit(cursor, (pygame.mouse.get_pos()))
                pygame.display.flip()
            elif not game_finished:
                finish_game(scale)
                break
        if restart:
            game_music.stop()
            restart = False
            game()
    game_music.stop()
    set_w_h_butt(*ex_size_)
    background_music.play()


def pass_function():
    pass


def training():
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    buttons_spr = pygame.sprite.Group()
    button1 = Button("BT_E.png", (2, 2), [""], "BT_E.png", alpha, lambda: slide_show())
    button1.update = pass_function
    slide_show()
    image = pygame.image.load("materials/img/BT_SLIDES.png").convert_alpha()
    image.set_colorkey(BLACK)
    button1.image_orig = image
    button1.image = image
    buttons_spr.add(button1)
    while running:
        tick.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_coordinates_rect(button1.rect, *event.pos):
                    button1.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                if in_coordinates_rect(button1.rect, *event.pos):
                    button1.target()
            if event.type == pygame.MOUSEMOTION:
                if in_coordinates_rect(button1.rect, *event.pos):
                    button1.target()
                else:
                    button1.target(0)
        mouse_pos = pygame.mouse.get_pos()
        if in_coordinates_rect(button1.rect, *mouse_pos):
            button1.target()
        else:
            button1.target(0)
        buttons_spr.update()
        screen.blit(slide, background_slide_rectangle)
        buttons_spr.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()


def slide_show():
    global back_ind, slide
    if back_ind == len(slides_list) - 1:
        global global_speed, global_speed_factor, global_level
        global_speed = 2
        global_speed_factor = 2
        gl1 = global_level
        global_level = (1, 2, 2, 0, 1, 40, 10, 2, 2, *ret_sizes(480, 600))
        game()
        global_level = gl1
        back_ind = -1
        raise ZeroDivisionError
    else:
        back_ind += 1
        slide = pygame.image.load(slides_list[back_ind]).convert_alpha()


def set_level(level_for_set, boxes):
    global global_level
    global_level = level_for_set
    boxes[0].text = "-" if global_level[0] < medium else "+"
    for i in range(1, len(boxes)):
        boxes[i].text = str(global_level[i])


def get_player_level(boxes):
    global player_level, global_level
    global_level = player_level
    boxes[0].text = "-" if player_level[0] < medium else "+"
    for i in range(1, len(boxes)):
        boxes[i].text = str(player_level[i])


def set_player_level(boxes):
    global player_level
    with suppress(Exception):
        player_current_level = player_level.copy()
        player_current_level[0] = normal if boxes[0].text == "-" else hard
        for i in range(1, len(player_level)):
            player_current_level[i] = int(boxes[i].text)
        set_level(player_current_level, boxes)
        player_level = player_current_level


def level_settings():
    global decorations
    input_box1 = InputBox(100, 100, main_but_sizes[9], main_but_sizes[8], "шары")
    input_box2 = InputBox(
        100,
        100 + main_but_sizes[9] + 5,
        main_but_sizes[9],
        main_but_sizes[8],
        "анифиры",
    )
    input_box3 = InputBox(
        100,
        100 + (main_but_sizes[9] + 5) * 2,
        main_but_sizes[9],
        main_but_sizes[8],
        "взрывные анифиры",
    )
    input_box4 = InputBox(
        100,
        100 + (main_but_sizes[9] + 5) * 3,
        main_but_sizes[9],
        main_but_sizes[8],
        "ложные взрывы(+/-)",
        doz="-+",
        doz_len=1,
    )
    input_box5 = InputBox(
        100,
        100 + (main_but_sizes[9] + 5) * 4,
        main_but_sizes[9],
        main_but_sizes[8],
        "цели",
    )
    input_box6 = InputBox(
        100,
        100 + (main_but_sizes[9] + 5) * 5,
        main_but_sizes[9],
        main_but_sizes[8],
        "заряды",
    )
    input_box7 = InputBox(
        main_but_sizes[6] * 6,
        100,
        main_but_sizes[9],
        main_but_sizes[8],
        "время раунда",
        doz_len=3,
    )
    input_box8 = InputBox(
        main_but_sizes[6] * 6,
        100 + main_but_sizes[9] + 5,
        main_but_sizes[9],
        main_but_sizes[8],
        "скорость",
        doz_len=3,
    )
    input_box9 = InputBox(
        main_but_sizes[6] * 6,
        100 + (main_but_sizes[9] + 5) * 2,
        main_but_sizes[9],
        main_but_sizes[8],
        "коэффициент скорости",
        doz_len=3,
    )
    input_box10 = InputBox(
        main_but_sizes[6] * 6,
        100 + (main_but_sizes[9] + 5) * 3,
        main_but_sizes[9],
        main_but_sizes[8],
        f"ширина поля(max:{str(size[0])})",
        doz_len=5,
    )
    input_box11 = InputBox(
        main_but_sizes[6] * 6,
        100 + (main_but_sizes[9] + 5) * 4,
        main_but_sizes[9],
        main_but_sizes[8],
        f"высота поля(max:{str(size[1])})",
        doz_len=4,
    )
    input_boxes = [
        input_box4,
        input_box1,
        input_box2,
        input_box3,
        input_box5,
        input_box6,
        input_box7,
        input_box8,
        input_box9,
        input_box10,
        input_box11,
    ]
    button = Button(
        "BSe.png",
        (main_but_sizes[0], main_but_sizes[1] + main_but_sizes[2] * 3),
        ["сохранить"],
        "NewButton.png",
        161,
        lambda: set_player_level(input_boxes),
        sz=17,
        font_size=44,
        animate_ind=0,
        animation_delay=1,
    )
    button1 = Button(
        "BSe.png",
        (20, main_but_sizes[7]),
        ["   3 из 10"],
        "NewButton.png",
        161,
        lambda: set_level(easy_level, input_boxes),
        sz=17,
        font_size=44,
        animate_ind=8,
        animation_delay=1,
    )
    button2 = Button(
        "BSe.png",
        (20 + 300, main_but_sizes[7]),
        ["   5 из 10"],
        "NewButton.png",
        161,
        lambda: set_level(normal_level, input_boxes),
        sz=17,
        font_size=44,
        animate_ind=16,
        animation_delay=1,
    )
    button3 = Button(
        "BSe.png",
        (20 + 300 * 2, main_but_sizes[7]),
        ["   7 из 10"],
        "NewButton.png",
        161,
        lambda: set_level(medium_level, input_boxes),
        sz=17,
        font_size=44,
        animate_ind=24,
        animation_delay=1,
    )
    button4 = Button(
        "BSe.png",
        (20 + 300 * 3, main_but_sizes[7]),
        ["   9 из 10"],
        "NewButton.png",
        161,
        lambda: set_level(hard_level, input_boxes),
        sz=17,
        font_size=44,
        animate_ind=32,
        animation_delay=1,
    )
    button5 = Button(
        "BSe.png",
        (20 + 300 * 4, main_but_sizes[7]),
        ["   11 из 10"],
        "NewButton.png",
        161,
        lambda: set_level(demon_level, input_boxes),
        sz=17,
        font_size=44,
        animate_ind=40,
        animation_delay=1,
    )
    button6 = Button(
        "BSe.png",
        (20 + 300 * 4, main_but_sizes[6] * 6 + main_but_sizes[9] + 5),
        ["     свой"],
        "NewButton.png",
        161,
        lambda: set_level(player_level, input_boxes),
        sz=17,
        font_size=44,
        animate_ind=48,
        animation_delay=1,
    )
    buttons_spr = pygame.sprite.Group()
    setting_buttons = [button, button1, button2, button3, button4, button5, button6]
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
                    if in_coordinates_rect(button.rect, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in setting_buttons:
                    if in_coordinates_rect(button.rect, *event.pos):
                        button.target()
        mouse_pos = pygame.mouse.get_pos()
        for button in setting_buttons:
            if in_coordinates_rect(button.rect, *mouse_pos):
                button.target()
            else:
                button.target(0)
        with suppress(Exception):
            if int(input_box10.text) > size[0] - 100:
                input_box10.text = str(size[0] - 100)
            if int(input_box11.text) > size[1] - 100:
                input_box11.text = str(size[1] - 100)
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
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
        clock.tick(FPS)


def set_width_and_height(w, h):
    w1, h1 = size[0] // 2, size[1] // 2
    global WIDTH_D, HEIGHT_D, WIDTH_U, HEIGHT_U
    WIDTH_D, HEIGHT_D = w1 + w // 2, h1 + h // 2
    WIDTH_U, HEIGHT_U = w1 - w // 2, h1 - h // 2


def set_w_h_butt(w, h):
    h += 3
    exit_buttonQ.rect[0] = w
    exit_buttonQ.rect[1] = h


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


def import_style():
    open_site("https://sites.google.com/view/eyesight-up-game", new=0)


def settings():
    global music_volume_sprites, decorations
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    d = "BS.png"
    buttons_spr = pygame.sprite.Group()
    button1 = Button(
        d,
        (main_but_sizes[0], main_but_sizes[1]),
        ["      стиль"],
        "BT_TEST.png",
        alpha,
        lambda: import_style(),
    )
    button3 = ButtonMusicControl(
        (main_but_sizes[5], main_but_sizes[6] * 3 - 2),
        "materials/img/Style/MusicControl/music_control_minus.png",
        alpha,
        lambda: minus_volume(),
    )
    button4 = ButtonMusicControl(
        (main_but_sizes[4], main_but_sizes[6] * 3 - 2),
        "materials/img/Style/MusicControl/music_control_plus.png",
        alpha,
        lambda: plus_volume(),
    )
    button2 = pygame.sprite.Sprite()
    draw_text(
        "materials/img/Style/buttons/BS.png",
        ["      звук"],
        54,
        "materials/img/Style/buttons/NewButton.png",
        30,
        30,
    )
    button2.image = pygame.image.load(
        "materials/img/Style/buttons/NewButton.png"
    ).convert_alpha()
    button2.rect = button2.image.get_rect()
    button2.rect.x, button2.rect.y = main_but_sizes[0], main_but_sizes[3]
    button2_ = pygame.sprite.Group(button2)
    main_settings_buttons = [button3, button4, button1]
    for button in main_settings_buttons:
        buttons_spr.add(button)
    while running:
        tick.tick(FPS)
        for event in pygame.event.get():
            running = event_test_exit(event)
            if not running:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in main_settings_buttons:
                    if in_coordinates_rect(button.rect, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in main_settings_buttons:
                    if in_coordinates_rect(button.rect, *event.pos):
                        button.target()
        mouse_pos = pygame.mouse.get_pos()
        for button in main_settings_buttons:
            if in_coordinates_rect(button.rect, *mouse_pos):
                button.target()
            else:
                button.target(0)
        buttons_spr.update()
        button_exit.update()
        decorations.update()
        background_music.play()
        screen.blit(back, back_rect)
        decorations.draw(screen)
        music_volume_sprites.draw(screen)
        button2_.draw(screen)
        buttons_spr.draw(screen)
        button_exit.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
    pygame.quit()


def set_style():
    global bt_dir, bg_dir, fg_dir, colors, sprites_to_colors, decorations, size
    decorations = pygame.sprite.Group()
    for i in range(2):
        decorations.add(
            set_speed_for_decoration_object(
                Figure(
                    pygame.image.load(fg_dir + "/ball2.png").convert_alpha(),
                    (0, size[0]),
                    (0, size[1]),
                )
            )
        )
    animated_figures_names = [
        "/FS_2_2.png",
        "/FS_2.png",
        "/FT4.png",
        "/prime_image_B.png",
        "/FT3.png",
        "/FT2.png",
    ]
    for i in range(5):
        for j in range(2):
            decorations.add(
                set_speed_for_decoration_object(
                    AnimatedFigure(
                        pygame.image.load(
                            fg_dir + animated_figures_names[i]
                        ).convert_alpha(),
                        (0, size[0]),
                        (0, size[1]),
                    )
                )
            )
    if not randrange(25):
        decorations.add(
            set_speed_for_decoration_object(
                AnimatedFigure(
                    pygame.image.load(fg_dir + "/FT_SPECIAL.png").convert_alpha(),
                    (0, size[0]),
                    (0, size[1]),
                )
            )
        )
    energy_image = pygame.image.load(fg_dir + "/score_chunk1.png").convert_alpha()
    for i in range(5):
        decorations.add(
            set_speed_for_decoration_object(
                AnimatedFigure(energy_image, (0, size[0]), (0, size[1]))
            )
        )
    pass


volume = 0
level = 0
with open("materials/data.csv", encoding="utf8") as csv_file:
    reader = csv.reader(csv_file, delimiter=";", quotechar='"')
    for index, q in enumerate(reader):
        if q[0] == "":
            break
        elif not index:
            level = [int(i) for i in q]
        elif index:
            player_level = [int(i) for i in q[:-3]]
            volume = float(q[-3])
            global_speed = int(q[-2])
            global_speed_factor = int(q[-1])

buttons, WIDTH_D, HEIGHT_D, WIDTH_U, HEIGHT_U, FPS, speed, BLACK = (
    [],
    0,
    0,
    0,
    0,
    60,
    6,
    (0, 0, 0),
)
speed_factor = 1

rotating_images = ["FT4.png"]
sc_im = "score_chunk1.png"
split_double_sprites = ["FT2.png", "FT3.png", "FS_2.png", "FS_2_2.png"]
animated_spr_list, split_sprites1_list, split_sprites2_list, rotating_sprites = (
    [],
    [],
    [],
    [],
)
not_rotated_images = ["ball2.png"]
not_rotated_sprites = []
game_process_sprites = pygame.sprite.Group()

bt_dir = "materials/img/Style/buttons/"
bg_dir = "materials/img/Style/backgrounds/"
fg_dir = "materials/img/Style/figures/"
put = "materials/Style"

pygame.init()
pygame.mixer.init()

pygame.mouse.set_visible(False)
cursor = pygame.image.load("materials\img\Style\cursor\cursor.png")

start_sound = pygame.mixer.Sound("materials/sounds/start_game_sound.ogg")
start_sound.set_volume(0.7)
win_sound = pygame.mixer.Sound("materials/sounds/win_game_sound.ogg")
lose_sound = pygame.mixer.Sound("materials/sounds/lose_game_sound.ogg")
incorrect_choice_sound = pygame.mixer.Sound(
    "materials/sounds/incorrect_choice_sound.ogg"
)
correct_choice_sound = pygame.mixer.Sound("materials/sounds/correct_choice_sound.ogg")
background_music = pygame.mixer.Sound("materials/sounds/background_music.ogg")
game_music = pygame.mixer.Sound("materials/sounds/game_music2.ogg")
game_music_list = (
    "materials/sounds/game_music1.ogg",
    "materials/sounds/game_music2.ogg",
    "materials/sounds/game_music3.ogg",
)
sounds = (
    start_sound,
    win_sound,
    lose_sound,
    incorrect_choice_sound,
    correct_choice_sound,
    background_music,
    game_music,
)

decorations = pygame.sprite.Group()
set_volume()
FONT = pygame.font.Font("materials/font.ttf", 32)
size = [GetSystemMetrics(0), GetSystemMetrics(1)]
coefficients = (1536 / size[0], 864 / size[1])
main_but_sizes = [
    ret_size_x(570),
    ret_size_y(132),
    ret_size_y(140),
    ret_size_y(272),
    ret_size_y(1010),
    ret_size_y(460),
    ret_size_y(100),
    ret_size_y(760),
    ret_size_y(24),
    ret_size_y(45),
]
ex_size_ = ret_sizes(main_but_sizes[4], main_but_sizes[1])
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Eyesight Up Game")
pygame.display.set_icon(
    pygame.image.load("materials/icon/active_exe_icon.png").convert_alpha()
)
clock = pygame.time.Clock()
set_style()
back = pygame.image.load(bg_dir + "g3.png").convert_alpha()
back_rect = back.get_rect()
colors = colorsS
sprites_to_colors = sprites_to_colorsS
easy = 1
normal = 2
medium = 3
hard = 4
demon = 5
COLOR_ACTIVE = pygame.Color(COLOR_ACTIVE_MAIN)
COLOR_INACTIVE = pygame.Color(COLOR_INACTIVE_MAIN)
FONT2 = pygame.font.Font("materials/font.ttf", main_but_sizes[8])
global_timer = 0
easy_level = (1, 3, 3, 0, 2, 1, 10, 2, 2, *ret_sizes(480, 600))
normal_level = (2, 3, 2, 2, 2, 2, 15, 2, 2, *ret_sizes(700, 720))
medium_level = (3, 3, 3, 3, 3, 2, 20, 2, 2, *ret_sizes(700, 720))
hard_level = (4, 3, 2, 5, 3, 3, 25, 3, 3, *ret_sizes(1436, 764))
demon_level = (5, 4, 4, 4, 4, 0, 30, 4, 4, *ret_sizes(1436, 764))
global_level = level
restart = False
music_image = pygame.image.load(
    "materials/img/music_control_count_image.png"
).convert_alpha()
exit_buttonQ = ButtonMusicControl(
    (ret_sizes(1481, 5)), "materials/img/Style/buttons/BT_E.png", 161, lambda x: x
)
button_exit = pygame.sprite.Group()
button_exit.add(exit_buttonQ)
slides_list = [
    f"materials/img/Style/slides/{i}" for i in listdir("materials/img/Style/slides")
]
slide = None
back_ind = -1
background_slide_rectangle = back_rect
errors_col_sprites = pygame.sprite.Group()
music_volume_sprites = pygame.sprite.Group()
help_volume()

back1 = pygame.image.load(bg_dir + "g_a.png").convert_alpha()
main_run = True

animation_steps = (0, 1, 1, 2, 2, 3, 4, 4)
steps_count = len(animation_steps)
start_sound.play()
for i in range(255, 0, -4):
    animated_background = back1.copy()
    animated_background.fill((i, i, i), special_flags=pygame.BLEND_RGB_ADD)
    screen.fill(BLACK)
    screen.blit(animated_background, back_rect)
    pygame.display.flip()
while main_run:
    with suppress(Exception):
        main_menu()
with open("materials/data.csv", "w", newline="", encoding="utf8") as csv_file:
    writer = csv.writer(
        csv_file, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    writer.writerow([*global_level])
    writer.writerow([*player_level, volume, global_speed, global_speed_factor])
remove("""materials/img/Style/buttons/NewButton.png""")

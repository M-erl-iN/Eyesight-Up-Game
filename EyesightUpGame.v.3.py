# EyesightUpGame
import copy
import csv
import json
import time
from contextlib import suppress
from math import sqrt
from os import listdir, remove
from random import choice, randrange, sample
from webbrowser import open as open_site

import pygame
from PIL import Image, ImageDraw, ImageFont
from screeninfo import get_monitors

from k import test
from materials.data.color_information import *


class QuestTablet(pygame.sprite.Sprite):
    def __init__(self):
        super(QuestTablet, self).__init__()
        self.quest_count = 12
        self.font_size = 30
        self.font = pygame.font.Font(
            "materials/data/Mariupol-Medium.ttf", self.font_size
        )
        self.quest_image = pygame.image.load(
            "materials/img/options/quest_.png"
        ).convert_alpha()
        self.matrix = self.generate_quest_matrix()
        self.text_x = 70 + self.quest_image.get_width() + 5
        self.reward_x = self.text_x + 300
        self.reward_image_x = self.reward_x + 30
        self.line_height = self.font_size + 28
        self.rect = pygame.rect.Rect(
            70, 170, 2000, self.line_height * self.quest_count + 170
        )
        self.rect_quest = None

    def generate_quest(self):
        return [
            self.quest_image,
            choice([0, 1, 2]),
            *self.generate_reward(randrange(2, 25)),
        ]

    def generate_reward(self, i):
        return i, i // 3 + 1

    def generate_quest_matrix(self):
        return [[self.generate_quest() for _ in range(self.quest_count)] for __ in range(3)]

    def draw_matrix(self, screen):
        for j in range(2, -1, -1):
            reward = self.font.render(str(self.matrix[0][0][3]), True, (0, 0, 0))

            self.rect_quest = [60 + j * (self.reward_image_x + 12) + reward.get_width() - 30,
                    None,
                    self.reward_image_x + reward.get_width() - 30,
                    self.line_height - 5]
            for i in range(len(self.matrix[0]) - 1, -1, -1):
                elem = self.matrix[j][i]
                y = (self.line_height + 5) * i + 170
                if elem[1] == 0:
                    text = f"Найди {elem[2]} целей"
                elif elem[1] == 1:
                    text = f"Потеряй {elem[2]} зарядов"
                else:
                    text = f"Заработай {elem[2]} монет"
                text = self.font.render(text, True, (0, 0, 0))
                reward = self.font.render(str(elem[3]), True, (0, 0, 0))

                self.rect_quest[1] = y - self.line_height // 6

                pygame.draw.rect(
                    screen,
                    (232, 255, 209),
                    self.rect_quest
                )
                screen.blit(
                    elem[0], (70 + j * (self.reward_image_x + 12) + reward.get_width() - 30, y)
                )

                screen.blit(
                    text,
                    (
                        self.text_x + j * (self.reward_image_x + 12) + reward.get_width() - 30,
                        y,
                    ),
                )

                screen.blit(
                    reward,
                    (
                        self.reward_x
                        + j * (self.reward_image_x + 12)
                        + reward.get_width()
                        - 30,
                        y,
                    ),
                )

                screen.blit(
                    options_images[1],
                    (
                        self.reward_image_x
                        + j * (self.reward_image_x + 12)
                        + reward.get_width()
                        - 30,
                        y,
                    ),
                )

    def clicked(self, pos):
        global quest
        pos = pos[0] - self.rect_quest[0], pos[1] - self.rect_quest[1]
        row = pos[1] // self.line_height
        col = pos[0] // self.rect_quest[2]
        if col > 2:
            col = 2
        if row > len(self.matrix[col]) - 1:
            row = len(self.matrix[col]) - 1
        font = pygame.font.Font(
            "materials/data/Mariupol-Medium.ttf", 44
        )
        current_quest_img = font.render('!', True, (0, 128, 64))
        print(col, row)
        self.matrix[col][row][0] = current_quest_img
        quest = Quest(self.matrix[col][row])


class Quest:
    def __init__(self, quest1):
        global quest_flag
        quest_flag = True
        self.start_time = time.time()
        self.arguments = quest1[1:]
        self.life_time = time.time() - self.start_time

    def update(self):
        global quest, quest_flag, new_primes, new_coins, new_errors
        self.life_time = time.time() - self.start_time
        if self.life_time > 10:
            del self
        if self.arguments[0] == 0:
            if new_primes >= self.arguments[1]:
                user_coins += self.arguments[2]
                quest_flag = False
                quest = None
                new_primes = 0
        if self.arguments[0] == 1:
            if new_coins >= self.arguments[1]:
                user_coins += self.arguments[2]
                quest_flag = False
                quest = None
                new_coins = 0
        if self.arguments[0] == 2:
            if new_errors >= self.arguments[1]:
                user_coins += self.arguments[2]
                quest_flag = False
                quest = None
                new_errors = 0


class Coins(pygame.sprite.Sprite):
    def __init__(self):
        super(Coins, self).__init__()
        self.image = options_images[1]
        self.font_size = self.image.get_width()
        self.counter = FONT.render(str(user_coins), True, (255, 255, 255))

    def update(self):
        self.counter = FONT.render(str(user_coins), True, (255, 255, 255))

    def draw(self, screen):
        screen.blit(self.counter, (80, 14))
        screen.blit(self.image, (80 + self.counter.get_width(), 14))


class BlockedObject(pygame.sprite.Sprite):
    def __init__(
        self, object_, image, cost, prompt, *function_arguments, function=None
    ):
        super(BlockedObject, self).__init__()
        self.font_size = 21
        self.func = function
        self.arguments = function_arguments
        if self.func is not None:
            self.clicked = self.clicked2
        else:
            self.clicked = self.clicked1
        FONT2 = pygame.font.Font("materials/data/UZSans-Medium.ttf", self.font_size)
        self.prompt = FONT2.render(prompt, True, (255, 255, 255))
        self.object = object_
        self.rect = object_.image.get_rect()
        self.rect.x = object_.rect.x
        self.rect.y = object_.rect.y
        self.cost = cost
        self.image = (
            object_.image
        )  # get_currency_image(image, 5, pygame.image.load('coin.png').convert_alpha())
        self.image.set_alpha(128)

    def clicked1(self, figures):
        global user_coins
        if user_coins > self.cost:
            user_coins -= self.cost
            figures.add(self.object)
            self.kill()

    def clicked2(self, figures):
        self.clicked1(figures)
        self.func(*self.arguments)

    def draw_prompt(self, canvas):
        pos = (
            self.rect.x + self.rect.width // 2 - self.prompt.get_width() // 2,
            self.rect.y + self.rect.height + self.font_size,
        )
        canvas.blit(
            self.prompt,
            (
                pos[0] + int(self.font_size / 5),
                pos[1] - int(self.font_size / 5 * 4),
            ),
        )


# Родительский класс для всех фигур
class Figure(pygame.sprite.Sprite):
    def __init__(self, image, width=None, height=None):
        #  назначение всех нужных переменных
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
        self.speed_y = rand_speed()
        self.speed_x = rand_speed()
        self.speeds_for_true_rotate = (abs(self.speed_x), abs(self.speed_y))
        self.became_prime = 0

    def update(self):
        #  обновление позиций фигур
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top < self.board_sizes[1][0]:
            self.speed_y = self.speeds_for_true_rotate[1]
        elif self.rect.bottom > self.board_sizes[1][1]:
            self.speed_y = -self.speeds_for_true_rotate[1]
        if self.rect.left < self.board_sizes[0][0]:
            self.speed_x = self.speeds_for_true_rotate[0]
        elif self.rect.right > self.board_sizes[0][1]:
            self.speed_x = -self.speeds_for_true_rotate[0]


class TextSprite(pygame.sprite.Sprite):
    def __init__(self, text, font, x, y):
        pygame.sprite.Sprite.__init__(self)
        font = pygame.font.Font(None, numbers_y["text_font_size"])
        self.image = font.render(text)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class AnimatedFigure(Figure):
    def __init__(self, image, width=0, height=0):
        #  назначение всех нужных переменных
        if width == 0:
            width = (WIDTH_U, WIDTH_D)
        if height == 0:
            height = (HEIGHT_U, HEIGHT_D)
        Figure.__init__(self, image, width, height)
        self.rot = 0
        self.rot_speed = rand_speed()
        self.last_update = pygame.time.get_ticks()

    def update(self):
        #  обновление позиций фигур
        self.rotate()
        Figure.update(self)

    def rotate(self):
        #  вращение изображения от оригинала
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
    def __init__(self, image, chunk, chunks_count, dif, inside_color, outside_color):
        super(SplitAnimatedFigure, self).__init__(image)
        self.chunks_count = chunks_count
        self.chunk = chunk
        self.inside_color, self.outside_color = inside_color, outside_color
        self.max_flash_radius = max(self.rect.width, self.rect.height) // 2
        self.flash_chance = 300 if dif > medium else 700
        self.flash_flag = False
        self.flash_radius = 0
        self.segmentation_flag = False
        self.disflash_image = pygame.surface.Surface(
            (self.max_flash_radius * 2 + 20, self.max_flash_radius * 2 + 20)
        )
        self.disflash_image.set_colorkey((0, 0, 0, 0))

    def update(self):
        super().update()
        if self.flash_flag:
            if not self.segmentation_flag:
                if self.flash_radius < self.max_flash_radius:
                    new_flash_radius = max(self.rect.width, self.rect.height) // 2
                    if new_flash_radius > self.max_flash_radius:
                        self.max_flash_radius = new_flash_radius
                    self.flash()
                elif self.flash_radius < self.max_flash_radius + 1:
                    flash_image = pygame.surface.Surface(
                        (self.max_flash_radius * 2 + 20, self.max_flash_radius * 2 + 20)
                    )
                    flash_image.set_colorkey((0, 0, 0, 0))
                    self.image = flash_image
                    x, y, w, h = (
                        self.rect.x,
                        self.rect.y,
                        self.rect.width,
                        self.rect.height,
                    )
                    self.rect = self.image.get_rect()
                    self.rect.x, self.rect.y = (
                        x - (self.rect.width - w) // 2,
                        y - (self.rect.height - h) // 2,
                    )
                    self.flash()
                elif self.flash_radius < self.max_flash_radius + 10:
                    self.flash()
                else:
                    self.disflash_image = pygame.surface.Surface(
                        (self.max_flash_radius * 2 + 20, self.max_flash_radius * 2 + 20)
                    )
                    self.disflash_image.set_colorkey((0, 0, 0, 0))
                    self.segmentation()
                    self.segmentation_flag = True
            elif self.segmentation_flag:
                if self.flash_radius > 0:
                    self.disflash()
                else:
                    self.kill()
        elif self.get_segmentation_chance() and not self.segmentation_flag:
            self.rotate = self.rotate_delete
            self.flash_flag = True

    def rotate_delete(self):
        pass

    def get_segmentation_chance(self):
        return not randrange(0, self.flash_chance)

    def segmentation(self):
        for i in range(self.chunks_count):
            i = copy.copy(self.chunk)
            i.rect.x, i.rect.y = self.rect.x, self.rect.y
            i.speed_x = rand_speed()
            i.speed_y = rand_speed()
            i.became_prime = self.became_prime
            game_process_sprites.add(i)
        game_process_sprites.remove(self)
        game_process_sprites.add(self)

    def flash(self):
        self.flash_radius += 1
        self.draw_circules()

    def draw_circules(self):
        x, y = self.rect.width // 2, self.rect.height // 2

        gradient_len = int(self.flash_radius // 2)

        pygame.draw.circle(self.image, self.inside_color, (x, y), gradient_len)

        r, g, b = self.inside_color
        r1, g1, b1 = self.outside_color
        r_, g_, b_ = (
            (r1 - r) / self.max_flash_radius,
            (g1 - g) / self.max_flash_radius,
            (b1 - b) / self.max_flash_radius,
        )
        for q in range(1, gradient_len):
            new_color = r + int(r_ * q), g + int(g_ * q), b + int(b_ * q)
            pygame.draw.circle(self.image, new_color, (x, y), gradient_len + q, 2)

    def disflash(self):
        self.flash_radius -= 1
        self.disflash_image.fill((0, 0, 0))
        self.disflash_image.set_colorkey((0, 0, 0, 0))
        self.image = self.disflash_image
        x, y = self.rect.x, self.rect.y
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.draw_circules()


class Slime(pygame.sprite.Sprite):
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

        self.rect.x = randrange(*width)
        self.rect.y = randrange(*height)

        self.x, self.y = self.rect.x, self.rect.y

        self.borders = (
            (width[0], width[1] - self.rect.width),
            (height[0], height[1] - self.rect.height),
        )

        self.start_pos = self.rect.x, self.rect.y

        self.last_wall = 5

        self.speed_x, self.speed_y, self.finish_pos, self.middle_pos = test(
            self.borders[0],
            self.borders[1],
            self.start_pos,
            global_speed,
            self.last_wall,
        )
        self.middle_x, self.middle_y = abs(self.start_pos[0] - self.middle_pos[0]), abs(
            self.start_pos[1] - self.middle_pos[1]
        )

        self.speed_flag_x = True
        self.speed_flag_y = True

        self.k = 1 + 0.0125 * sqrt(global_speed_factor * global_speed)

        self.became_prime = 0

    def update(self):
        self.board_hit()
        if self.speed_flag_x:
            if not (
                self.x - abs(self.speed_x)
                < self.middle_pos[0]
                < self.x + abs(self.speed_x)
            ):
                self.speed_x *= self.k
            else:
                self.speed_flag_x = False
        else:
            self.speed_x /= self.k
        if self.speed_flag_y:
            if not (
                self.y - abs(self.speed_y)
                < self.middle_pos[1]
                < self.y + abs(self.speed_y)
            ):
                self.speed_y *= self.k
            else:
                self.speed_flag_y = False
        else:
            self.speed_y /= self.k

        self.x += self.speed_x
        self.y += self.speed_y

        self.rect.x, self.rect.y = self.x, self.y

    def board_hit(self):
        w0, h0 = self.x < self.borders[0][0], self.y < self.borders[1][0]
        w1, h1 = self.x > self.borders[0][1], self.y > self.borders[1][1]
        if w0 or w1 or h0 or h1:
            if w0:
                self.last_wall = 1
                self.x = self.borders[0][0]
            if w1:
                self.last_wall = 3
                self.x = self.borders[0][1]
            if h0:
                self.last_wall = 2
                self.y = self.borders[1][0]
            if h1:
                self.last_wall = 4
                self.y = self.borders[1][1]
            self.rect.x, self.rect.y = self.x, self.y
            self.start_pos = (self.rect.x, self.rect.y)
            self.speed_flag_x = True
            self.speed_flag_y = True
            self.speed_x, self.speed_y, self.finish_pos, self.middle_pos = test(
                self.borders[0],
                self.borders[1],
                self.start_pos,
                global_speed,
                self.last_wall,
            )
            self.image = self.image_orig


class Button(pygame.sprite.Sprite):
    def __init__(
        self,
        image,
        pos,
        button_text,
        alpha,
        func,
        font_size=54,
        x=30,
        tr=1,
        sz=30,
        animate_ind=0,
        animation_delay=0,
    ):
        #  создание изображения по шаблону и надписи для кнопки
        self.animate_ind = animate_ind
        self.animation_delay = animation_delay
        pygame.sprite.Sprite.__init__(self)
        self.current_animation_step = 1
        self.route = 1
        self.route_animate = 1
        self.route_animate_delay = 1
        self.animation_time = 1 * 6
        self.current_animation_time = 0
        self.image_orig = draw_text(image, button_text[0], font_size_for_main_buttons)
        self.alpha = alpha
        self.func = func
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
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
        #  изменение прозрачности и позиции при наведении и нажатии
        self.image.set_alpha(self.alpha + (255 - self.alpha) // 3 * (3 - i))
        if i == 2 and not self.was_targeted:
            self.was_targeted = 1
        elif i == 0 and self.was_targeted:
            self.was_targeted = 0

    def clicked(self):
        #  запуск переданной функции
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
        #  установка шага смещения вниз при наведении
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


#  кнопка, независящая от надписи
class MiniButton(Button):
    def __init__(self, pos, image, alpha, func, tr=1):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = image
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


#  реализация ввода с клавиатуры
class InputBox:
    def __init__(self, x, y, w, h, parameter, doz="0123456789", doz_len=2):
        self.doz = doz
        self.doz_len = doz_len
        self.rect = pygame.Rect(x, y, w, h)
        self.rect2 = self.rect.copy()
        self.rect2[1] += 7
        self.color = COLOR_INACTIVE
        self.parameter = FONT2.render(parameter, True, COLOR_ACTIVE)
        self.par_x = self.parameter.get_size()[0] + 24
        self.rect2[0] += self.par_x
        self.text = ""
        self.active = False
        self.txt_surface = None

    def handle_event(self, event):
        #  обработка ввода с клавиатуры
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
        width = max(
            numbers_x["input_box_width"],
            self.txt_surface.get_width() + int(self.rect.w / 5),
        )
        self.rect2.w = width
        self.rect.w = width

    def draw(self, canvas):
        canvas.blit(
            self.parameter,
            (self.rect.x + int(self.rect.w / 5), self.rect.y + int(self.rect.w / 5)),
        )
        canvas.blit(
            self.txt_surface,
            (
                self.rect.x + int(self.rect.w / 5) + self.par_x,
                self.rect.y + int(self.rect.w / 5),
            ),
        )
        pygame.draw.rect(canvas, self.color, self.rect2, 2)


def draw_text(image, text, font_size):
    image_path = "test/drawing_text.png"
    image_size = image.get_size()
    pygame.image.save(image, image_path)

    image_pil = Image.open(image_path)
    draw = ImageDraw.Draw(image_pil)

    font = ImageFont.truetype("materials/data/UZSans-Medium.ttf", font_size)

    text_size = draw.textsize(text, font)

    draw.text(
        ((image_size[0] - text_size[0]) / 2, (image_size[1] - text_size[1]) / 2),
        text,
        font=font,
    )

    image_pil.save(image_path)

    image_and_text = pygame.image.load(image_path).convert_alpha()
    remove(image_path)
    return image_and_text


def get_currency_image(image, cost, currency_image):
    image_path = "test/drawing_cost.png"
    image_size = image.get_size()
    currency_path = "test/drawing_currency.png"
    currency_size = currency_image.get_size()
    pygame.image.save(image, image_path)
    pygame.image.save(currency_image, currency_path)

    image_pil = Image.open(image_path)
    currency_image_pil = Image.open(currency_path)

    draw = ImageDraw.Draw(image_pil)

    font = ImageFont.truetype("materials/data/UZSans-Medium.ttf", font_size)

    text_size = draw.textsize(cost, font)

    a = (image_size[0] - text_size[0]) / 2
    b = (image_size[1] - currency_size[1]) / 2

    draw.text(
        (a - currency_size[0] / 2, (image_size[1] - text_size[1]) / 2),
        cost,
        font=font,
    )

    pixels = image_pil.load()
    currency_pixels = currency_image_pil.load()

    for x in range(currency_size[0]):
        for y in range(currency_size[1]):
            currency_pixel = currency_pixels[x, y]
            pixels[x + a, y + b] = currency_pixel

    image_pil.save(image_path)

    image_cost = pygame.image.load(image_path).convert_alpha()
    # remove(image_path)
    remove(currency_path)
    return image_cost


#  коэффициент перезаписи изображений под пользовательский экран
def set_factor_for_img(img_name):
    img = Image.open(img_name)
    x, y = img.size
    if x != screen_size[0] or y != screen_size[1]:
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
    obj.speed_x, obj.speed_y = speeds
    obj.speeds_for_true_rotate = (abs(speeds[0]), abs(speeds[1]))
    return obj


def event_test_exit(event):
    if event.type == pygame.QUIT:
        set_w_h_butt(*ex_size_)
        return False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return False
    if event.type == pygame.MOUSEBUTTONDOWN:
        if in_image(exit_buttonQ, *event.pos):
            set_w_h_butt(*ex_size_)
            return False
    if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
        if in_image(exit_buttonQ, *event.pos):
            exit_buttonQ.target()
    if event.type == pygame.MOUSEMOTION:
        if in_image(exit_buttonQ, *event.pos):
            exit_buttonQ.target()
        else:
            exit_buttonQ.target(0)
    return True


def in_coordinates_rect(rect, x, y):
    return rect.x < x < rect.x + rect.width and rect.y < y < rect.y + rect.height


def in_image(game_object, x1, y1):
    rect = game_object.rect
    if in_coordinates_rect(rect, x1, y1):
        x, y = x1 - rect.x, y1 - rect.y
        pixel = game_object.image.get_at((x, y))
        return pixel[3] != 0
    return 0


def main_menu():
    global back, back_rect, exit_buttonQ, button_exit, back1, split_sprites1_list, split_sprites2_list, rotating_sprites, not_rotated_sprites, decorations
    split_sprites2_list = []
    split_sprites1_list = []
    rotating_sprites = []
    not_rotated_sprites = []

    for i in not_rotated_ids:
        not_rotated_sprites.append(figure_images[i])

    for i in rotating_ids:
        rotating_sprites.append(figure_images[i])

    for i in range(0, len(split_ids), 2):
        split_sprites1_list.append(
            (figure_images[split_ids[i]], sprites_to_colors[split_ids[i]])
        )
        split_sprites2_list.append(figure_images[split_ids[i + 1]])
    background_music.play()
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    buttons_spr = pygame.sprite.Group()

    button1 = Button(
        button_images[1],
        (main_button_x, main_button_start_y),
        ["играть"],
        alpha,
        lambda: game(),
        animation_delay=1,
    )
    button2 = Button(
        button_images[1],
        (main_button_x, main_button_start_y + main_button_step_y),
        ["уровень"],
        alpha,
        lambda: level_settings(),
        animate_ind=8,
        animation_delay=1,
    )
    button3 = Button(
        button_images[1],
        (main_button_x, main_button_start_y + main_button_step_y * 2),
        ["задания"],
        alpha,
        quests,
        animate_ind=16,
        animation_delay=1,
    )
    main_buttons = [button1, button2, button3]
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
                    if in_image(button, *event.pos):
                        button.clicked()
                for option in list(options_sprites):
                    if in_image(option, *event.pos):
                        option.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in main_buttons:
                    if in_image(button, *event.pos):
                        button.target()
                for option in list(options_sprites):
                    if in_image(option, *event.pos):
                        option.target()
        mouse_pos = pygame.mouse.get_pos()
        for button in main_buttons:
            if in_image(button, *mouse_pos):
                button.target()
            else:
                button.target(0)
        for option in list(options_sprites):
            if in_image(option, *mouse_pos):
                option.target()
            else:
                option.target(0)
        buttons_spr.update()
        button_exit.update()
        decorations.update()
        coins.update()
        options_sprites.update()
        background_music.play()
        screen.blit(back, back_rect)
        decorations.draw(screen)
        buttons_spr.draw(screen)
        button_exit.draw(screen)
        options_sprites.draw(screen)
        coins.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
    pygame.quit()


def start_game(list__):
    global restart
    list_ = list__.copy()
    spr_start = pygame.sprite.Group()
    im = figure_images[4]
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
        coins.update()
        screen.blit(back, back_rect)
        button_exit.draw(screen)
        game_process_sprites.draw(screen)
        spr_start.draw(screen)
        errors_col_sprites.draw(screen)
        coins.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
    spr_start.clear(screen, back)
    for i in list_:
        i.image = i.image_orig
        i.became_prime = 1
    return True


def finish_game(false, coins_rewind):
    global restart, user_coins, new_errors, new_primes, new_coins
    im = figure_images[4].copy()
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
                        if in_image(i, x, y):
                            if i.became_prime:
                                if quest_flag:
                                    new_primes += 1
                                true_clicks += 1
                                correct_choice_sound.play()
                                i.image = im
                                i.image_orig = im
                                i.rect.screen_size = im_size
                            else:
                                false_clicks += 1
                                incorrect_choice_sound.play()
                                errors_energy[-1].kill()
                                errors_energy = errors_energy[:-1]
                                if quest_flag:
                                    new_errors += 1
                                i.kill()
                            break
            if false_clicks == false:
                game_music.stop()
                lose_sound.play()
                break
            elif true_clicks == true:
                game_process_sprites.draw(screen)
                screen.blit(cursor, (pygame.mouse.get_pos()))
                pygame.display.flip()
                time.sleep(0.25)
                game_music.stop()
                win_sound.play()
                user_coins += coins_rewind
                if quest_flag:
                    new_coins += coins_rewind
                break
        coins.update()
        button_exit.draw(screen)
        game_process_sprites.draw(screen)
        errors_col_sprites.draw(screen)
        coins.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()


def game():
    global game_process_sprites, animated_spr_list, split_sprites1_list, split_sprites2_list, errors_col_sprites, game_music, global_level, global_speed_factor, volume, global_timer, global_speed
    game_process_sprites, animated_spr_list = pygame.sprite.Group(), []
    errors_col_sprites = pygame.sprite.Group()
    (
        difficulty,
        not_rot_col,
        rot_col,
        spl_rot_col,
        slime_col,
        prime_col,
        scale,
        global_timer,
        global_speed,
        global_speed_factor,
        (w),
        h,
        coins_rewind,
    ) = global_level
    set_width_and_height(w, h)
    set_w_h_butt(
        WIDTH_D - numbers_x["width_exit_button"],
        HEIGHT_U - numbers_y["height_exit_button"],
    )
    error_image = figure_images[3].copy()
    scale_for_cycle = scale
    scale_j = scale_for_cycle // 16 + 1
    for j in range(scale_j):
        if scale_for_cycle > 16:
            scale_i = 16
        else:
            scale_i = scale % 16
            if scale_for_cycle % 16 == 0 and scale_for_cycle != 0:
                scale_i = 16
        for i in range(scale_i):
            d = pygame.sprite.Sprite()
            d.image = error_image
            d.rect = [
                WIDTH_D + j * numbers_y["error_y"],
                HEIGHT_U + numbers_y["error_y"] * i,
                error_image.get_width(),
                error_image.get_height(),
            ]
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
            AnimatedFigure(a),
            1 + randrange(3),
            difficulty,
            *split_sprites1_list[d][1],
        )
        game_process_sprites.add(c)
        animated_spr_list.append(c)

    for i in range(rot_col):
        if not randrange(0, 5000):
            c = AnimatedFigure(figure_images[3].copy())
        else:
            d = randrange(0, len(rotating_ids))
            c = AnimatedFigure(rotating_sprites[d])
        game_process_sprites.add(c)

    for i in range(slime_col):
        game_process_sprites.add(Slime(figure_images[0]))
    background_music.stop()
    game_music = pygame.mixer.Sound(choice(game_music_list))
    game_music.set_volume(volume)
    game_music.play()
    a1 = sample(list(game_process_sprites), prime_col)

    starting = start_game(a1)
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
                    game_process_sprites = pygame.sprite.Group()
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
                coins.update()
                screen.blit(back, back_rect)
                game_process_sprites.draw(screen)
                errors_col_sprites.draw(screen)
                button_exit.update()
                button_exit.draw(screen)
                coins.draw(screen)
                screen.blit(cursor, (pygame.mouse.get_pos()))
                pygame.display.flip()
            elif not game_finished:
                finish_game(scale, coins_rewind)
                break
        if restart:
            game_music.stop()
            restart = False
            starting = False
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
    button1 = Button(
        button_images[2], (16, 24), [""], alpha, lambda: slide_show(), animation_delay=1
    )
    slide_show()
    image = button_images[2]
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
                if in_image(button1, *event.pos):
                    button1.clicked()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    button1.clicked()
                if event.key == pygame.K_LEFT:
                    slide_back()
            if event.type == pygame.MOUSEBUTTONUP:
                if in_image(button1, *event.pos):
                    button1.target()
            if event.type == pygame.MOUSEMOTION:
                if in_image(button1, *event.pos):
                    button1.target()
                else:
                    button1.target(0)
        mouse_pos = pygame.mouse.get_pos()
        if in_image(button1, *mouse_pos):
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
        global_level = (1, 2, 2, 0, 1, 1, 40, 10, 2, 2, *ret_sizes(480, 600), 0)
        game()
        global_level = gl1
        back_ind = -1
        raise ZeroDivisionError
    else:
        back_ind += 1
        slide = slides_images[back_ind]


def slide_back():
    global back_ind, slide
    back_ind -= 1
    slide = slides_images[back_ind]


def set_level(level_for_set):
    global global_level
    global_level = level_for_set


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
        set_level(player_current_level)
        player_level = player_current_level


def level_settings():
    global decorations
    # input_box1 = InputBox(100, 100, 25, 24, "шары") # x, y, w, h
    # input_box2 = InputBox(
    #     100,
    #     100 + 30,
    #     25,
    #     24,
    #     "анифиры",
    # )
    # input_box3 = InputBox(
    #     100,
    #     100 + 30 * 2,
    #     25,
    #     24,
    #     "взрывные анифиры",
    # )
    # input_box4 = InputBox(
    #     100,
    #     100 + 30 * 3,
    #     25,
    #     24,
    #     "ложные взрывы(+/-)",
    #     doz="-+",
    #     doz_len=1,
    # )
    # input_box5 = InputBox(
    #     100,
    #     100 + 30 * 4,
    #     25,
    #     24,
    #     "цели",
    # )
    # input_box6 = InputBox(
    #     100,
    #     100 + 30 * 5,
    #     25,
    #     24,
    #     "заряды",
    # )
    # input_box7 = InputBox(
    #     100 * 6,
    #     100,
    #     25,
    #     24,
    #     "время раунда",
    #     doz_len=3,
    # )
    # input_box8 = InputBox(
    #     100 * 6,
    #     100 + 30,
    #     25,
    #     24,
    #     "скорость",
    #     doz_len=3,
    # )
    # input_box9 = InputBox(
    #     100 * 6,
    #     100 + 30 * 2,
    #     25,
    #     24,
    #     "коэффициент скорости",
    #     doz_len=3,
    # )
    # input_box10 = InputBox(
    #     100 * 6,
    #     100 + 30 * 3,
    #     25,
    #     24,
    #     f"ширина поля(max:{str(screen_size[0])})",
    #     doz_len=5,
    # )
    # input_box11 = InputBox(
    #     100 * 6,
    #     100 + 30 * 4,
    #     25,
    #     24,
    #     f"высота поля(max:{str(screen_size[1])})",
    #     doz_len=4,
    # )
    # input_boxes = [
    #     input_box4,
    #     input_box1,
    #     input_box2,
    #     input_box3,
    #     input_box5,
    #     input_box6,
    #     input_box7,
    #     input_box8,
    #     input_box9,
    #     input_box10,
    #     input_box11,
    # ]
    # button = Button(
    #     d,
    #     (570, 132 + 140 * 3),
    #     ["сохранить"],
    #     161,
    #     lambda: set_player_level(input_boxes),
    #     sz=17,
    #     font_size=44,
    #     animate_ind=0,
    #     animation_delay=1,
    # )

    set_w_h_butt(*exit_button_angle_pos)

    done = True

    while done:
        screen.blit(back, back_rect)
        for event in pygame.event.get():
            done = event_test_exit(event)
            # for box in input_boxes:
            #     box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in list(level_setting_buttons):
                    if in_image(button, *event.pos):
                        button.clicked()
                for button in list(level_setting_blocked_buttons):
                    if in_image(button, *event.pos):
                        button.clicked(level_setting_buttons)
                if in_image(level_back_button, *event.pos):
                    done = False
            if event.type == pygame.MOUSEBUTTONUP:
                for button in level_setting_buttons:
                    if in_image(button, *event.pos):
                        button.target()
            if not done:
                return
        mouse_pos = pygame.mouse.get_pos()
        for button in level_setting_buttons:
            if in_image(button, *mouse_pos):
                button.target()
            else:
                button.target(0)
        # with suppress(Exception):
        #     if int(input_box10.text) > screen_size[0] - 100:
        #         input_box10.text = str(screen_size[0] - 100)
        #     if int(input_box11.text) > screen_size[1] - 100:
        #         input_box11.text = str(screen_size[1] - 100)

        coins.update()
        level_setting_buttons.update()
        level_setting_blocked_buttons.update()
        button_exit.update()
        decorations.update()
        decorations.draw(screen)
        level_setting_buttons.draw(screen)
        level_setting_blocked_buttons.draw(screen)
        button_exit.draw(screen)
        # for box in input_boxes:
        #     box.update()
        # for box in input_boxes:
        #     box.draw(screen)
        for i in list(level_setting_blocked_buttons):
            i.draw_prompt(screen)

        coins.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
        clock.tick(FPS)


def set_width_and_height(w, h):
    w1, h1 = screen_size[0] // 2, screen_size[1] // 2
    global WIDTH_D, HEIGHT_D, WIDTH_U, HEIGHT_U
    WIDTH_D, HEIGHT_D = w1 + w // 2, h1 + h // 2
    WIDTH_U, HEIGHT_U = w1 - w // 2, h1 - h // 2


def set_w_h_butt(w, h):
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
        d.rect = [
            (475 + 60 * i) / coefficients[0],
            80 / coefficients[1],
            43 / coefficients[0],
            25 / coefficients[1],
        ]
        music_volume_sprites.add(d)


def turn_up_volume():
    global volume
    if volume < 1.0:
        volume = volume + 0.1
        set_volume()
        help_volume()


def turn_down_volume():
    global volume
    if volume > 0.0:
        volume = volume - 0.1
        set_volume()
        help_volume()


def import_style():
    open_site("https://sites.google.com/view/eyesight-up-game", new=0)


def quests():
    set_width_and_height(*ret_sizes(700, 520))
    set_w_h_butt(
        WIDTH_D - numbers_x["width_exit_button"],
        HEIGHT_U - numbers_y["height_exit_button"],
    )
    running = True
    tick = pygame.time.Clock()
    quest_board = QuestTablet()
    while running:
        tick.tick(FPS)
        for event in pygame.event.get():
            running = event_test_exit(event)
            if not running:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if in_coordinates_rect(quest_board.rect, *event.pos):
                    quest_board.clicked(event.pos)
        coins.update()
        button_exit.update()
        decorations.update()
        background_music.play()
        screen.blit(back, back_rect)
        decorations.draw(screen)
        quest_board.draw_matrix(screen)
        button_exit.draw(screen)
        coins.draw(screen)
        screen.blit(cursor, (pygame.mouse.get_pos()))
        pygame.display.flip()
    pygame.quit()


def settings():
    global music_volume_sprites, decorations
    alpha = 161
    running = True
    tick = pygame.time.Clock()
    button_image = button_images[1]
    buttons_spr = pygame.sprite.Group()
    button1 = Button(
        button_image,
        (main_button_x, main_button_start_y),
        ["проект"],
        alpha,
        lambda: import_style(),
    )
    button3 = MiniButton(
        (numbers_x["volume_control_minus_x"], numbers_y["volume_control_y"]),
        music_control_images[1],
        alpha,
        lambda: turn_down_volume(),
    )
    button4 = MiniButton(
        (numbers_x["volume_control_plus_x"], numbers_y["volume_control_y"]),
        music_control_images[2],
        alpha,
        lambda: turn_up_volume(),
    )
    button2 = pygame.sprite.Sprite()
    button2.image = draw_text(button_image, "звук", font_size_for_main_buttons)
    button2.rect = button2.image.get_rect()
    button2.rect.x, button2.rect.y = (
        main_button_x,
        main_button_start_y + main_button_step_y,
    )
    button2_ = pygame.sprite.Group(button2)
    main_settings_buttons = [button1, button3, button4]
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
                    if in_image(button, *event.pos):
                        button.clicked()
            if event.type == pygame.MOUSEBUTTONUP:
                for button in main_settings_buttons:
                    if in_image(button, *event.pos):
                        button.target()
        mouse_pos = pygame.mouse.get_pos()
        for button in main_settings_buttons:
            if in_image(button, *mouse_pos):
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
    global bt_dir, bg_dir, fg_dir, colors, sprites_to_colors, decorations, screen_size
    decorations = pygame.sprite.Group()
    for i in range(2):
        decorations.add(
            set_speed_for_decoration_object(
                Figure(
                    figure_images[0],
                    (0, screen_size[0]),
                    (0, screen_size[1]),
                )
            )
        )

    for i in range(6):
        for j in range(2):
            decorations.add(
                set_speed_for_decoration_object(
                    AnimatedFigure(
                        figure_images[i],
                        (0, screen_size[0]),
                        (0, screen_size[1]),
                    )
                )
            )
    if not randrange(500):
        decorations.add(
            set_speed_for_decoration_object(
                AnimatedFigure(
                    figure_images[2],
                    (0, screen_size[0]),
                    (0, screen_size[1]),
                )
            )
        )
    for i in range(6):
        decorations.add(
            set_speed_for_decoration_object(
                AnimatedFigure(
                    figure_images[3].copy(), (0, screen_size[0]), (0, screen_size[1])
                )
            )
        )
    pass


def images_resize(dir, screen_size, attitudes_filename):
    with open(attitudes_filename, encoding="utf8") as resize_images_file:
        resize_images = json.load(resize_images_file)
    images = []
    for image in resize_images:
        final_image_size = list(map(lambda x: x * screen_size[0], resize_images[image]))
        final_image_size[0] = int(final_image_size[0]) + 1
        final_image_size[1] = int(final_image_size[1]) + 1
        resized_image = pygame.image.load(dir + image).convert_alpha()
        resized_image = pygame.transform.scale(resized_image, final_image_size)
        images.append(resized_image)
    return images


def set_first_blocked_level(level, group=None, object_=None):
    global first_blocked_level
    first_blocked_level = level
    if group is not None:
        group.add(object_)


if __name__ == "__main__":
    volume = 0
    level = 0

    with open("materials/data/informarion.json") as file:
        information = json.load(file)

    level = information["global_level"]
    player_level = information["player_level"]
    volume = information["volume"]
    global_speed = information["global_speed"]
    global_speed_factor = information["global_speed_factor"]
    user_coins = information["coins"]
    completed_achievements_ids = information["achievements_ids"]
    first_blocked_level = information["blocked_level"]
    last_quest_update_time = information["last_quest_update_time"]

    buttons, WIDTH_D, HEIGHT_D, WIDTH_U, HEIGHT_U, FPS, BLACK = (
        [],
        0,
        0,
        0,
        0,
        60,
        (0, 0, 0),
    )
    speed_factor = 1

    # ----------------------
    #        INITS
    # ----------------------

    pygame.init()
    pygame.mixer.init()
    pygame.display.init()

    # ----------------------
    #       MONITOR
    # ----------------------

    active_monitor = get_monitors()[0]
    screen_size = (active_monitor.width, active_monitor.height)
    print(screen_size)

    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Eyesight Up Game", "materials/icon/active_exe_icon.png")
    pygame.display.set_icon(
        pygame.image.load("materials/icon/active_exe_icon.png").convert_alpha()
    )

    coefficients = (1536 / screen_size[0], 864 / screen_size[1])

    pixel_x = 1 / coefficients[0]
    pixel_y = 1 / coefficients[1]

    pixel_xy = 2 / (coefficients[0] + coefficients[1])
    pixel_20xy = 2 / (coefficients[0] + coefficients[1])

    with open("numbers.json", "r") as file:
        numbers = json.load(file)

    for i in numbers:
        numbers[i] *= pixel_xy

    with open("numbers_x.json", "r") as file:
        numbers_x = json.load(file)

    for i in numbers_x:
        numbers_x[i] /= coefficients[0]

    with open("numbers_y.json", "r") as file:
        numbers_y = json.load(file)

    for i in numbers_y:
        numbers_y[i] /= coefficients[1]

    speed = numbers["speed"]

    pygame.mouse.set_visible(False)

    # ----------------------
    #     IMAGE RESIZING
    # ----------------------

    bt_dir = "materials/img/buttons/"
    bg_dir = "materials/img/backgrounds/"
    fg_dir = "materials/img/figures/"
    mc_dir = "materials/img/music_control/"
    cur_dir = "materials/img/cursor/"
    sl_dir = "materials/img/slides/"
    op_dir = "materials/img/options/"

    background_images = images_resize(
        bg_dir, screen_size, "materials/data/attitudes/background_attitudes.json"
    )
    button_images = images_resize(
        bt_dir, screen_size, "materials/data/attitudes/button_attitudes.json"
    )
    cursor_image = [
        pygame.image.load("materials/img/cursor/cursor.png").convert_alpha()
    ]
    figure_images = images_resize(
        fg_dir, screen_size, "materials/data/attitudes/figure_attitudes.json"
    )
    music_control_images = images_resize(
        mc_dir, screen_size, "materials/data/attitudes/music_control_attitudes.json"
    )
    slides_images = images_resize(
        sl_dir, screen_size, "materials/data/attitudes/slide_attitudes.json"
    )
    options_images = images_resize(
        op_dir, screen_size, "materials/data/attitudes/options_attitudes.json"
    )

    # ----------------------
    #    FONT CORRECTION
    # ----------------------

    new_primes = 0
    new_coins = 0
    new_errors = 0
    quest_flag = False
    quest = None

    # ----------------------
    #    FONT CORRECTION
    # ----------------------

    font_size_for_main_buttons = int(54 / coefficients[1])
    font_size = int(32 / coefficients[1])
    FONT = pygame.font.Font("materials/data/UZSans-Medium.ttf", font_size)
    print(coefficients)

    # ----------------------
    #    POSITIONS CORRECTION
    # ----------------------

    main_button_x = screen_size[0] / 2 - button_images[1].get_width() / 2
    main_button_start_y = screen_size[1] / 6.5
    main_button_step_y = screen_size[1] / 6.2

    # ----------------------
    #       OPTIONS
    # ----------------------
    buttons_x = numbers_x["option_indent"] // 3

    setting_button = MiniButton((buttons_x, buttons_x), button_images[3], 161, settings)
    training_button = MiniButton(
        (buttons_x, buttons_x + button_images[3].get_height()),
        button_images[4],
        161,
        training,
    )

    coins = Coins()

    options_sprites = pygame.sprite.Group()
    options_sprites.add(setting_button)
    options_sprites.add(training_button)

    # ----------------------
    #    LEVEL SCREEN
    # ----------------------

    level_button1 = Button(
        button_images[1],
        (
            screen_size[0] / 2 - screen_size[0] / 6 - button_images[1].get_width() / 2,
            screen_size[1] / 4 - button_images[1].get_height() / 2,
        ),
        ["новичек"],
        161,
        lambda: set_level(easy_level),
        sz=17,
        font_size=44,
        animate_ind=8,
        animation_delay=1,
    )

    level_button2 = Button(
        button_images[1],
        (
            screen_size[0] / 2 + screen_size[0] / 6 - button_images[1].get_width() / 2,
            screen_size[1] / 4 - button_images[1].get_height() / 2,
        ),
        ["легкий"],
        161,
        lambda: set_level(normal_level),
        sz=17,
        font_size=44,
        animate_ind=16,
        animation_delay=1,
    )
    level_button3 = Button(
        button_images[1],
        (
            screen_size[0] / 2 + screen_size[0] / 3 - button_images[1].get_width() / 2,
            screen_size[1] / 2 - button_images[1].get_height() / 2,
        ),
        ["средний"],
        161,
        lambda: set_level(medium_level),
        sz=17,
        font_size=44,
        animate_ind=24,
        animation_delay=1,
    )
    level_button4 = Button(
        button_images[1],
        (
            screen_size[0] / 2 + screen_size[0] / 6 - button_images[1].get_width() / 2,
            screen_size[1] / 4 * 3 - button_images[1].get_height() / 2,
        ),
        ["сложный"],
        161,
        lambda: set_level(hard_level),
        sz=17,
        font_size=44,
        animate_ind=32,
        animation_delay=1,
    )
    level_button5 = Button(
        button_images[1],
        (
            screen_size[0] / 2 - screen_size[0] / 6 - button_images[1].get_width() / 2,
            screen_size[1] / 4 * 3 - button_images[1].get_height() / 2,
        ),
        ["кошмар"],
        161,
        lambda: set_level(demon_level),
        sz=17,
        font_size=44,
        animate_ind=40,
        animation_delay=1,
    )
    level_button6 = Button(
        button_images[1],
        (
            screen_size[0] / 2 - screen_size[0] / 3 - button_images[1].get_width() / 2,
            screen_size[1] / 2 - button_images[1].get_height() / 2,
        ),
        ["свой"],
        161,
        lambda: set_level(player_level),
        sz=17,
        font_size=44,
        animate_ind=48,
        animation_delay=1,
    )

    level_back_button = Button(
        button_images[1],
        (
            screen_size[0] / 2 - button_images[1].get_width() / 2,
            screen_size[1] / 2 - button_images[1].get_height() / 2,
        ),
        ["назад"],
        161,
        lambda x: x / 0,
        sz=17,
        font_size=44,
        animation_delay=1,
    )

    level_setting_buttons = pygame.sprite.Group(level_button1, level_back_button)
    level_setting_blocked_buttons = pygame.sprite.Group()

    if first_blocked_level < 6:
        level_button6 = BlockedObject(
            level_button6,
            button_images[1],
            2000,
            "20 ДОСТИЖЕНИЙ",
            6,
            function=set_first_blocked_level,
        )
        if first_blocked_level == 5:
            level_setting_blocked_buttons.add(level_button6)
    elif first_blocked_level > 5:
        level_setting_buttons.add(level_button6)

    if first_blocked_level < 5:
        level_button5 = BlockedObject(
            level_button5,
            button_images[1],
            200,
            "200 МОНЕТ И 10 ДОСТИЖЕНИЙ",
            5,
            level_setting_blocked_buttons,
            level_button6,
            function=set_first_blocked_level,
        )
        if first_blocked_level == 4:
            level_setting_blocked_buttons.add(level_button5)
    elif first_blocked_level > 4:
        level_setting_buttons.add(level_button5)

    if first_blocked_level < 4:
        level_button4 = BlockedObject(
            level_button4,
            button_images[1],
            100,
            "100 МОНЕТ И 5 ДОСТИЖЕНИЙ",
            4,
            level_setting_blocked_buttons,
            level_button5,
            function=set_first_blocked_level,
        )
        if first_blocked_level == 3:
            level_setting_blocked_buttons.add(level_button4)
    elif first_blocked_level > 3:
        level_setting_buttons.add(level_button4)

    if first_blocked_level < 3:
        level_button3 = BlockedObject(
            level_button3,
            button_images[1],
            45,
            "45 МОНЕТ И 3 ДОСТИЖЕНИЙ",
            3,
            level_setting_blocked_buttons,
            level_button4,
            function=set_first_blocked_level,
        )
        if first_blocked_level == 2:
            level_setting_blocked_buttons.add(level_button3)
    elif first_blocked_level > 2:
        level_setting_buttons.add(level_button3)

    if first_blocked_level < 2:
        level_button2 = BlockedObject(
            level_button2,
            button_images[1],
            10,
            "10 МОНЕТ И 1 ДОСТИЖЕНИЕ",
            2,
            level_setting_blocked_buttons,
            level_button3,
            function=set_first_blocked_level,
        )
        if first_blocked_level == 1:
            level_setting_blocked_buttons.add(level_button2)
    elif first_blocked_level > 1:
        level_setting_buttons.add(level_button2)

    # ----------------------

    rotating_ids = [5]
    split_ids = [6, 8, 7, 9]
    animated_spr_list = []
    split_sprites1_list = []
    split_sprites2_list = []
    rotating_sprites = []
    not_rotated_ids = [0]
    not_rotated_sprites = []
    game_process_sprites = pygame.sprite.Group()

    put = "materials/Style"

    cursor = cursor_image[0]

    start_sound = pygame.mixer.Sound("materials/sounds/start_game_sound.ogg")
    start_sound.set_volume(0.7)
    win_sound = pygame.mixer.Sound("materials/sounds/win_game_sound.ogg")
    lose_sound = pygame.mixer.Sound("materials/sounds/lose_game_sound.ogg")
    incorrect_choice_sound = pygame.mixer.Sound(
        "materials/sounds/incorrect_choice_sound.ogg"
    )
    correct_choice_sound = pygame.mixer.Sound(
        "materials/sounds/correct_choice_sound.ogg"
    )
    background_music = pygame.mixer.Sound("materials/sounds/background_music.mp3")
    game_music = pygame.mixer.Sound("materials/sounds/game_music2.ogg")
    game_music_list = (
        "materials/sounds/game_music3.mp3",
        "materials/sounds/game_music5.mp3",
        "materials/sounds/game_music4.mp3",
        "materials/sounds/game_music2.ogg",
        "materials/sounds/game_music1.ogg",
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
    ex_size_ = ret_sizes(1010, 132)
    exit_button_angle_pos = ret_sizes(1481, 5)
    clock = pygame.time.Clock()
    set_style()
    back = background_images[0]
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
    FONT2 = pygame.font.Font("materials/data/font.ttf", 24)
    global_timer = 0
    easy_level = (1, 3, 3, 0, 0, 2, 1, 10, 2, 2, *ret_sizes(480, 600), 1)
    normal_level = (2, 2, 2, 2, 1, 2, 2, 15, 2, 2, *ret_sizes(700, 720), 3)
    medium_level = (3, 2, 3, 3, 2, 2, 2, 20, 2, 2, *ret_sizes(700, 720), 5)
    hard_level = (4, 2, 2, 4, 3, 3, 3, 25, 3, 3, *ret_sizes(1436, 764), 10)
    demon_level = (5, 2, 2, 4, 4, 4, 0, 30, 4, 4, *ret_sizes(1436, 764), 40)
    """difficulty,
        not_rot_col,
        rot_col,
        spl_rot_col,
        slime_col,
        prime_col,
        scale,
        global_timer,
        global_speed,
        global_speed_factor,
        (w),
        h,
        coins"""
    global_level = level
    restart = False
    music_image = music_control_images[0]
    exit_buttonQ = MiniButton((ret_sizes(1481, 5)), button_images[0], 161, lambda x: x)
    button_exit = pygame.sprite.Group()
    button_exit.add(exit_buttonQ)
    slides_list = [f"materials/img/slides/{i}" for i in listdir("materials/img/slides")]
    slide = None
    back_ind = -1
    background_slide_rectangle = back_rect
    errors_col_sprites = pygame.sprite.Group()
    music_volume_sprites = pygame.sprite.Group()
    help_volume()

    back1 = pygame.image.load(bg_dir + "flash_background.png").convert_alpha()

    main_run = True

    animation_steps = (0, 1, 1, 2, 2, 3, 4, 4)
    steps_count = len(animation_steps)
    # start_sound.play()
    # for i in range(255, 0, -5):
    #     animated_background = back1.copy()
    #     animated_background.fill((i, i, i), special_flags=pygame.BLEND_RGB_ADD)
    #     screen.fill(BLACK)
    #     screen.blit(animated_background, back_rect)
    #     pygame.display.flip()

    while main_run:
        with suppress(Exception):
            main_menu()

    information["global_level"] = global_level
    information["player_level"] = player_level
    information["volume"] = volume
    information["global_speed"] = global_speed
    information["global_speed_factor"] = global_speed_factor
    information["coins"] = user_coins
    information["achievements_ids"] = completed_achievements_ids
    information["blocked_level"] = first_blocked_level
    information["last_quest_update_time"] = last_quest_update_time

    with open("materials/data/informarion.json", "w") as file:
        json.dump(information, file)

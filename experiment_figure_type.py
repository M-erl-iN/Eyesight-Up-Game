import time
from math import atan, pow, sin, sqrt
from random import choice, random, randrange

import pygame


class QuestTablet(pygame.sprite.Sprite):
    def __init__(self):
        super(QuestTablet, self).__init__()
        self.quest_count = 25
        self.font_size = 30
        self.font = pygame.font.Font("materials/data/font.ttf", self.font_size)
        self.quest_image = pygame.image.load(
            "materials/img/options/quest_.png"
        ).convert_alpha()
        self.matrix = self.generate_quest_matrix()
        self.text_x = 70 + self.quest_image.get_width() + 5
        self.reward_x = self.text_x + 560
        self.reward_image_x = self.reward_x + 100
        self.line_height = self.font_size + 8
        self.rect = pygame.rect.Rect(
            70, 100, 2000, self.line_height * self.quest_count + 100
        )

    def generate_quest(self):
        return (
            self.quest_image,
            choice([0, 1, 2]),
            *self.generate_reward(randrange(3, 12)),
        )

    def generate_reward(self, i):
        return i, i // 3 + 1

    def generate_quest_matrix(self):
        return [self.generate_quest() for _ in range(self.quest_count)]

    def draw_matrix(self, screen):
        for i in range(len(self.matrix)):
            elem = self.matrix[i]
            y = self.line_height * i + 100
            screen.blit(elem[0], (70, y))
            if elem[1] == 0:
                text = f"Найди {elem[2]} целей"
            elif elem[1] == 1:
                text = f"Потеряй {elem[2]} зарядов"
            else:
                text = f"Заработай {elem[2]} монет"
            text = self.font.render(text, True, (255, 255, 255))
            reward = self.font.render(elem[3], True, (255, 255, 255))

            screen.blit(elem[0], (70, y))

            screen.blit(text, (self.text_x, y))

            screen.blit(reward, (self.reward_x, y))

            screen.blit(coin, (self.reward_image_x, y))

    def clicked(self, pos):
        global quest
        pos = pos[0] - 70, pos[1] - 100
        id = pos[1] // self.line_height
        quest = Quest(self.matrix[id])


class Quest:
    def __init__(self, quest1):
        global quest_flag
        quest_flag = True
        self.start_time = time.time()
        self.arguments = quest1[1:]
        self.life_time = time.time() - self.start_time

    def update(self):
        global quest, quest_flag
        self.life_time = time.time() - self.start_time
        if self.life_time > 10:
            del self
        if self.arguments[0] == 0:
            if new_primes >= self.arguments[1]:
                user_coins += self.arguments[2]
                quest_flag = False
                quest = None
        if self.arguments[0] == 1:
            if new_coins >= self.arguments[1]:
                user_coins += self.arguments[2]
                quest_flag = False
                quest = None
        if self.arguments[0] == 2:
            if new_errors >= self.arguments[1]:
                user_coins += self.arguments[2]
                quest_flag = False
                quest = None


pygame.init()

clock = pygame.time.Clock()
fps1 = 60

screen_size = (600, 600)
screen = pygame.display.set_mode(screen_size)

running = True

figures = pygame.sprite.Group()

blocked_figures = pygame.sprite.Group()

global_speed_factor = 3
global_speed = 3

ball = pygame.image.load("materials/img/figures/ball.png").convert_alpha()
ball = pygame.transform.scale(ball, (60, 60))

while running:
    clock.tick(fps1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in list(figures):
                if in_image(i, *event.pos):
                    i.clicked()
            for i in list(blocked_figures):
                if in_image(i, *event.pos):
                    i.clicked(figures)
    figures.update()
    coins.update()
    blocked_figures.update()

    screen.fill((0, 35, 35))
    coins.draw(screen)
    pygame.display.flip()

pygame.quit()
quit()

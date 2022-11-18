from os import remove

import pygame
from PIL import Image, ImageDraw, ImageFont


def get_currency_image(image, cost, currency_image):
    cost = str(cost)
    image_path = "test/drawing_cost.png"
    image_size = image.get_size()
    image.set_alpha(196)

    currency_path = "test/drawing_currency.png"
    currency_size = currency_image.get_size()
    pygame.image.save(image, image_path)
    pygame.image.save(currency_image, currency_path)

    image_pil = Image.open(image_path)
    currency_image_pil = Image.open(currency_path)

    draw = ImageDraw.Draw(image_pil)

    font_size = int(currency_image.get_width())
    font = ImageFont.truetype("materials/data/UZSans-Medium.ttf", font_size)

    text_size = draw.textsize(cost, font)

    a = (image_size[0] - text_size[0]) / 2
    b = (image_size[1] - currency_size[1]) / 2
    c = int((image_size[0] + text_size[0]) / 2)

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
            print(currency_pixel)
            if currency_pixel != (0, 0, 0, 0):
                pixels[x + c, y + b] = currency_pixel

    image_pil.save(image_path)

    image_cost = pygame.image.load(image_path).convert_alpha()
    # remove(image_path)
    remove(currency_path)
    return image_cost


if __name__ == "__main__":
    pygame.init()
    pygame.display.init()

    screen = pygame.display.set_mode((100, 100))

    coin = pygame.image.load("coin.png").convert_alpha()
    coin.set_colorkey((0, 0, 0, 0))

    get_currency_image(
        pygame.image.load("materials/img/buttons/main_button.png").convert_alpha(),
        195,
        pygame.image.load("coin.png").convert_alpha(),
    )

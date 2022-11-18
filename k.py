import time
from math import atan, degrees, radians, sin, sqrt, tan
from random import choice, random, randrange, shuffle

from numba import jit, njit


# @jit(forceobj=True)
def test(board_w, board_h, first_point, speed_radius, last_wall):
    first_point = [float(first_point[0]), float(first_point[1])]
    speed_x = randrange(100, 500) / 500
    speed_y = sqrt(1 - pow(speed_x, 2))

    speeds = [speed_x, speed_y]
    shuffle(speeds)

    speed_x, speed_y = speeds

    speed_x *= speed_radius
    speed_y *= speed_radius

    # speed_x = 6
    k = choice([-1, 1])
    if last_wall == 1:
        speed_y = abs(speed_y)
        speed_x *= k
    elif last_wall == 2:
        speed_x = -abs(speed_x)
        speed_y *= k
    elif last_wall == 3:
        speed_y = -abs(speed_y)
        speed_x *= k
    elif last_wall == 4:
        speed_x = abs(speed_x)
        speed_y *= k
    x, y = first_point[0], first_point[1]
    second_point = cicle(board_w, board_h, x, y, speed_x, speed_y)

    middle_point = get_middle_point(first_point, second_point)
    return speed_x, speed_y, second_point, middle_point


def get_middle_point(first_point, second_point):
    return (first_point[0] + second_point[0]) / 2, (
        first_point[1] + second_point[1]
    ) / 2


# @jit(nopython=True)
def cicle(board_w, board_h, x, y, speed_x, speed_y):
    while board_w[0] <= x <= board_w[1] and board_h[0] <= y <= board_h[1]:
        x += speed_x
        y += speed_y
    second_point = (x - speed_x, y - speed_y)
    return second_point

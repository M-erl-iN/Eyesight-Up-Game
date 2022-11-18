from math import atan, degrees, radians, sin, sqrt, tan
from random import randrange


def my_sin(alpha):  # in degrees
    return round(sin(radians(alpha)), 4)


def cot(alpha):
    return 1 / tan(alpha)


def test(w, h, alpha, o):
    a0 = o[0], 0
    b1 = w, o[1]
    a1 = o[0], h
    b0 = 0, o[1]

    q1, q2, q3, q4 = (0, 0), (w, 0), (w, h), (0, h)

    delta1 = round(degrees(atan(b1[1] / (b1[0] - o[0]))))
    delta2 = round(180 - degrees(atan(b0[1] / o[0])))
    delta3 = round(180 + degrees(atan((q4[1] - b0[1]) / o[0])))
    delta4 = round(360 - degrees(atan((q3[1] - b1[1]) / (b1[0] - o[0]))))

    second_point = [0, 0]
    if alpha < delta1 or delta4 <= alpha:
        x = w - o[0]
        y = cot(radians(alpha)) * x

    if delta1 <= alpha < delta2:
        y = o[1]
        x = cot(radians(alpha)) * o[1]

    if delta2 <= alpha < delta3:
        x = o[0]
        y = cot(radians(alpha)) * x

    if delta3 <= alpha < delta4:
        y = h - o[1]
        x = cot(radians(alpha)) * y

    second_point[0] = o[0] + x
    second_point[1] = o[1] + y

    z_in_2 = x**2 + y**2
    z0 = speed_radius**2

    k = sqrt(z0) / sqrt(z_in_2)
    x0 = round(x * k, 1)
    y0 = round(y * k, 1)

    print(x0, y0)


w, h = 1536, 1224
alpha = 160
my_position = (w / 2, h / 2)


global_speed = 3
global_speed_factor = 3

speed_radius = global_speed * global_speed_factor

o = my_position

for i in range(10):
    test(w, h, randrange(360), (randrange(0, w), randrange(0, h)))

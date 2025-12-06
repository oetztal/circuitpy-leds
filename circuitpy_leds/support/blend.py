import time

from circuitpy_leds import Strip


def multiply_tuple(values: tuple, factor: float) -> tuple:
    return tuple(value * factor for value in values)


def add_tuples(tuple1: tuple, tuple2: tuple):
    if len(tuple1) is not len(tuple2):
        return None  # this type of addition is not defined for tuples with different lengths

    sum_of_two = []
    for i in range(len(tuple1)):
        sum_of_two.append(tuple1[i] + tuple2[i])
    return tuple(sum_of_two)


def power_blend(power: float, start_color: tuple, end_color: tuple, fade_progress: float) -> tuple:
    start_component = multiply_tuple(start_color, fade_progress ** power)
    target_component = multiply_tuple(end_color, (1 - fade_progress) ** power)
    return add_tuples(start_component, target_component)


def linear_blend(start_color: tuple, end_color: tuple, fade_progress: float) -> tuple:
    return power_blend(1, start_color, end_color, fade_progress)


class SmoothBlend:

    def __init__(self, strip: Strip, target_colors: tuple | list[tuple]):
        self.strip = strip
        self.target_colors = target_colors if isinstance(target_colors, list) else [target_colors] * len(strip)
        self.start_time = time.monotonic()
        self.initial_colors = [strip[i] for i in range(len(strip))]

    def step(self):
        print("step")
        now = time.monotonic()
        fade_progress = 1.0 - min((now - self.start_time) / 2.0, 1.0)

        for led_num in range(len(self.strip)):
            # print("blend", now, led_num, fade_progress)
            color = linear_blend(self.initial_colors[led_num], self.target_colors[led_num], fade_progress)
            if led_num == 0:
                print(color)
            self.strip[led_num] = color

        self.strip.show()

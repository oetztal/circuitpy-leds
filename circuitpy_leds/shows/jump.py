#!/usr/bin/env python3
import asyncio
import math

from circuitpy_leds import Strip


class Ball(object):

    def __init__(self, height, stripe, color):
        self.height = height - stripe
        self.stripe = stripe
        self.width = 2 * math.sqrt(self.height)
        self.center = self.width / 2.0
        self.color = color
        self.period = 0
        self.next = False

    def get_pos(self, t):
        current_period = int(math.floor(t / self.width))

        if self.period != current_period:
            self.period = current_period
            self.next = True

        return int(self.height - (t % self.width - self.center) ** 2)

    def is_next(self):
        if self.next:
            # log.debug("next %d", self.height)
            self.next = False
            return True
        return False


class Jump:
    """\
    Jumping dots
    """

    def __init__(self, strip: Strip, pause_sec=0.005):
        self.strip = strip
        self.num_leds = len(strip)

        self.state = {}
        self.stripe = 1
        self.spare_colors = [(0, 255, 255)]

        self.balls = (
            Ball(self.num_leds, self.stripe, (255, 0, 0)),
            Ball(self.num_leds * 0.5, self.stripe, (0, 255, 0)),
            Ball(self.num_leds * 0.75, self.stripe, (255, 255, 0)),
            Ball(self.num_leds * 0.88, self.stripe, (255, 0, 255)),
            Ball(self.num_leds * 0.66, self.stripe, (0, 0, 255))
        )

        self.pause_sec = pause_sec

    async def execute(self, index: int):
        t = index * 0.1

        self.strip.fill((0, 0, 0))

        for offset in range(0, self.stripe):
            for ball in self.balls:
                pos = ball.get_pos(t)
                index = pos + offset
                self.strip[index] = ball.color

                if ball.is_next():
                    self.spare_colors.insert(0, ball.color)
                    ball.color = self.spare_colors.pop()

        self.strip.show()
        await asyncio.sleep(self.pause_sec)

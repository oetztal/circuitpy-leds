import asyncio
import random
import time

from .. import Strip
from ..support import probability_of


class Starlight:

    def __init__(self, strip: Strip, probability: float = 0.1, length: float = 5, fade: float = 1):
        self.strip = strip
        self.num_leds = len(strip)
        self.color = (255, 180, 50)
        self.state = {}
        self.probability = probability
        self.length = length
        self.fade = fade

    async def execute(self, index: int):
        now = time.monotonic()

        if probability_of(self.probability):
            self.state[random.randint(0, self.num_leds - 1)] = now

        self.state = {pos: start for pos, start in self.state.items() if (start + 2 * self.fade + self.length) > now}

        self.strip.fill((0, 0, 0))
        for pos, start in self.state.items():
            seconds = now - start
            if seconds < self.fade:
                brightness = seconds / self.fade
            elif seconds < (self.length + self.fade):
                brightness = 1.0
            elif seconds < (self.length + 2 * self.fade):
                brightness = 1.0 - (seconds - self.fade - self.length) / self.fade
            else:
                brightness = 0.0

            self.strip[pos] = tuple(int(c * brightness) for c in self.color)

        self.strip.show()
        await asyncio.sleep(0.05)

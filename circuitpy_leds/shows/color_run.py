import asyncio
import random

from circuitpy_leds.config import Config


class ColorRun:

    def __init__(self, config: Config):
        self.num_leds = config.num_leds
        value = 255
        self.phases = [(value, 0, 0), (0, value, 0), (0, 0, value), (value, value, 0), (value, 0, value),
                       (0, value, value), (value, value, value)]
        self.state = []

    async def execute(self, pixels, index):

        if random.randint(0, 100) > 95:
            color = random.choice(self.phases)
            speed = random.randint(20, 60) / 100
            self.state.append((index, speed, color))

        pixels.fill((0, 0, 0))
        self.state = [(start, speed, color) for (start, speed, color) in self.state if
                      int((index - start) * speed) < self.num_leds]
        for (start, speed, color) in self.state:
            pixels[int((index - start) * speed)] = color

        pixels.show()
        await asyncio.sleep(0)

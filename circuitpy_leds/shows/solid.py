import asyncio

from circuitpy_leds.config import Config
from ..support.blend import SmoothBlend


class Solid:

    def __init__(self, _: Config, color: tuple):
        self.color = color
        self.blend = None


    async def execute(self, pixels, index):
        if self.blend is None:
            self.blend = SmoothBlend(pixels, self.color)

        self.blend.step()

        await asyncio.sleep(0.1)

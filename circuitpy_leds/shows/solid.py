import asyncio

from .. import Strip
from ..support.blend import SmoothBlend


class Solid:

    def __init__(self, strip: Strip, color: tuple):
        self.strip = strip
        self.color = color
        self.blend = None


    async def execute(self, _):
        if self.blend is None:
            self.blend = SmoothBlend(self.strip, self.color)

        self.blend.step()

        await asyncio.sleep(0.1)

import asyncio

from .. import Strip
from ..support.blend import SmoothBlend
from ..support.color import validate_color


class Solid:

    def __init__(self, strip: Strip, color: list[int] | tuple = (255, 255, 255)):
        self.strip = strip
        self.color = validate_color(color)
        self.blend = None

    async def execute(self, _):
        if self.blend is None:
            self.blend = SmoothBlend(self.strip, self.color)

        self.blend.step()

        await asyncio.sleep(0.1)

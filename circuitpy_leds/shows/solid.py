import asyncio

from .. import Strip
from ..support.blend import SmoothBlend


class Solid:
    """
    Solid color effect with smooth blending transition.

    Displays a single solid color across all LEDs with a smooth fade-in
    transition from the current state to the target color.

    :param strip: The LED strip to control
    :param color: RGB color tuple (red, green, blue) with values 0-255
    """

    def __init__(self, strip: Strip, color: tuple):
        self.strip = strip
        self.color = color
        self.blend = None

    async def execute(self, _):
        """
        Execute one step of the solid color blend.

        Initializes the blend on first call, then steps through the transition.

        :param _: Unused step parameter (required by show interface)
        """
        if self.blend is None:
            self.blend = SmoothBlend(self.strip, self.color)

        self.blend.step()

        await asyncio.sleep(0.05)

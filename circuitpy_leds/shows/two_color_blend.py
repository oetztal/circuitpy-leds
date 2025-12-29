import asyncio

from .. import Strip
from ..support.blend import SmoothBlend
from ..support.color import linear_dim, add_tuples


class TwoColorBlend:
    """
    Smooth gradient blend between two colors across the LED strip.

    Creates a linear gradient from one color at the start of the strip to
    another color at the end, with smooth color transitions in between.
    Uses smooth blending for fade-in from current state.

    :param strip: The LED strip to control
    :param color1: RGB color tuple for the start of the strip (0-255)
    :param color2: RGB color tuple for the end of the strip (0-255)
    """

    def __init__(self, strip: Strip, color1, color2):
        self.strip = strip
        self.num_leds = len(strip)
        self.color1 = color1
        self.color2 = color2
        self.blend = None

    async def execute(self, index):
        """
        Execute one step of the two-color blend animation.

        Initializes the gradient on first call, then steps through the transition.

        :param index: Current animation step (unused)
        """
        if self.blend is None:
            target_colors = []
            for led in range(self.num_leds):
                normal_distance = led / (self.num_leds - 1) if self.num_leds > 1 else 0
                component1 = linear_dim(self.color1, 1 - normal_distance)
                component2 = linear_dim(self.color2, normal_distance)
                led_color = add_tuples(component1, component2)
                target_colors.append(led_color)
            self.blend = SmoothBlend(self.strip, target_colors)

        self.blend.step()

        await asyncio.sleep(0.1)

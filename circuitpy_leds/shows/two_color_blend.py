import asyncio

from ..config import Config
from ..support.color import linear_dim, add_tuples
from ..support.blend import SmoothBlend


class TwoColorBlend:

    def __init__(self, config: Config, color1, color2):
        self.num_leds = config.num_leds
        self.color1 = color1
        self.color2 = color2
        self.blend = None

    async def execute(self, pixels, index):
        if self.blend is None:
            target_colors = []
            for led in range(self.num_leds):
                normal_distance = led / (self.num_leds - 1) if self.num_leds > 1 else 0
                component1 = linear_dim(self.color1, 1 - normal_distance)
                component2 = linear_dim(self.color2, normal_distance)
                led_color = add_tuples(component1, component2)
                target_colors.append(led_color)
            self.blend = SmoothBlend(pixels, target_colors)

        self.blend.step()

        await asyncio.sleep(0.1)

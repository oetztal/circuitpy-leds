import asyncio

from circuitpy_leds import Strip
from circuitpy_leds.config import Config
from circuitpy_leds.support.color import wheel


class Rainbow:
    """
    Rainbow color wheel effect that rotates through the full color spectrum.

    Creates a smooth gradient that cycles through red, green, blue and all
    colors in between, with the pattern continuously rotating along the strip.

    :param strip: The LED strip to control
    """

    def __init__(self, strip: Strip):
        self.strip = strip
        self.num_leds = len(strip)
        self.scale_factor = 255 / self.num_leds

    async def execute(self, current_step):
        """
        Execute one step of the rainbow animation.

        :param current_step: Current animation step for rotation
        """
        scale_factor = 255 / self.num_leds  # Value for the index change between two neighboring LEDs
        start_index = current_step % 255  # Value of LED 0
        for i in range(self.num_leds):
            led_index = start_index + i * scale_factor  # Index of LED i, not rounded and not wrapped at 255
            # Get the actual color out of wheel
            self.strip[i] = wheel(led_index % 255)
        self.strip.show()
        await asyncio.sleep(0.002)


import asyncio

from circuitpy_leds import Strip
from circuitpy_leds.config import Config
from circuitpy_leds.support.color import wheel


class Rainbow:

    def __init__(self, strip: Strip):
        self.strip = strip
        self.num_leds = len(strip)
        self.scale_factor = 255 / self.num_leds

    async def execute(self, current_step):
        scale_factor = 255 / self.num_leds  # Value for the index change between two neighboring LEDs
        start_index = current_step % 255  # Value of LED 0
        for i in range(self.num_leds):
            led_index = start_index + i * scale_factor  # Index of LED i, not rounded and not wrapped at 255
            pixel_color = wheel(led_index % 255)  # Get the actual color out of wheel
            self.strip[i] = pixel_color
        self.strip.show()
        await asyncio.sleep(0.002)


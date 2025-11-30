import asyncio
import random

from circuitpy_leds.config import Config
from .. import Strip
from ..support.color import wheel


class TheaterChase:

    def __init__(self, strip: Strip, num_steps_per_cycle=21):
        print(f"TheaterChase initialized {num_steps_per_cycle}")
        self.strip = strip
        self.num_leds = len(strip)
        self.num_steps_per_cycle = num_steps_per_cycle
        self.state = []

    async def execute(self, index):
        # One cycle = One trip through the color wheel, 0..254
        # Few cycles = quick transition, lots of cycles = slow transition
        # Note: For a smooth transition between cycles, numStepsPerCycle must be a multiple of 7
        start_index = index % 7  # Each segment is 7 dots long: 2 blank, and 5 filled
        cycle_pos = (index % self.num_steps_per_cycle) / self.num_steps_per_cycle
        value = int(round(cycle_pos * 255.0, 0))
        color_index = wheel(value)
        for pixel in range(self.num_leds):
            # Two LEDs out of 7 are blank. At each step, the blank ones move one pixel ahead.
            if ((pixel + start_index) % 7 == 0) or ((pixel + start_index) % 7 == 1):
                self.strip[pixel] = (0, 0, 0)
            else:
                self.strip[pixel] = color_index

        self.strip.show()
        await asyncio.sleep(0)

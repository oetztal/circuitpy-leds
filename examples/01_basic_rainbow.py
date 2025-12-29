"""
Basic Rainbow Effect Example

This example demonstrates the simplest way to run a rainbow effect on an LED strip.
"""

import asyncio
from circuitpy_leds import Strip
from circuitpy_leds.shows import Rainbow


# Mock strip for testing (replace with actual hardware)
class MockStrip(Strip):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.leds = [(0, 0, 0)] * num_leds

    def __len__(self):
        return self.num_leds

    def __setitem__(self, index, value):
        self.leds[index] = value
        print(f"LED {index}: RGB{value}")

    def __getitem__(self, index):
        return self.leds[index]

    def fill(self, color):
        for i in range(self.num_leds):
            self.leds[i] = color

    def show(self):
        # In real hardware, this sends data to the physical LEDs
        pass


async def main():
    # Create a strip with 30 LEDs
    strip = MockStrip(30)

    # Create rainbow effect
    rainbow = Rainbow(strip)

    print("Running rainbow effect... Press Ctrl+C to stop")

    try:
        step = 0
        while True:
            await rainbow.execute(step)
            step += 1
    except KeyboardInterrupt:
        print("\nStopping rainbow effect")
        strip.fill((0, 0, 0))
        strip.show()


if __name__ == "__main__":
    asyncio.run(main())

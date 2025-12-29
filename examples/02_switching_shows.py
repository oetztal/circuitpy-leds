"""
Switching Between Shows Example

This example demonstrates how to switch between different LED effects.
"""

import asyncio
from circuitpy_leds import Strip
from circuitpy_leds.shows import Rainbow, Solid, TheaterChase


class MockStrip(Strip):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.leds = [(0, 0, 0)] * num_leds

    def __len__(self):
        return self.num_leds

    def __setitem__(self, index, value):
        self.leds[index] = value

    def __getitem__(self, index):
        return self.leds[index]

    def fill(self, color):
        for i in range(self.num_leds):
            self.leds[i] = color

    def show(self):
        pass


async def run_show(show, steps, name):
    """Run a show for a specified number of steps"""
    print(f"\nRunning {name} for {steps} steps...")
    for step in range(steps):
        await show.execute(step)
        if step % 50 == 0:
            print(f"  Step {step}/{steps}")


async def main():
    strip = MockStrip(60)

    # Create different shows
    shows = [
        (Solid(strip, (255, 0, 0)), 100, "Red Solid"),
        (Rainbow(strip), 200, "Rainbow"),
        (Solid(strip, (0, 255, 0)), 100, "Green Solid"),
        (TheaterChase(strip), 200, "Theater Chase"),
        (Solid(strip, (0, 0, 255)), 100, "Blue Solid"),
    ]

    print("Cycling through shows... Press Ctrl+C to stop")

    try:
        while True:
            for show, steps, name in shows:
                await run_show(show, steps, name)
    except KeyboardInterrupt:
        print("\n\nStopping show cycle")
        strip.fill((0, 0, 0))
        strip.show()


if __name__ == "__main__":
    asyncio.run(main())

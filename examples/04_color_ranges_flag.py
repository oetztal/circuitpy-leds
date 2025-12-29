"""
ColorRanges - Flag Display Example

This example demonstrates how to use ColorRanges to display flags or
multi-color sections on an LED strip.
"""

import asyncio
from circuitpy_leds import Strip
from circuitpy_leds.shows import ColorRanges


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
        # Print a simple visualization
        bar = "█" * 2
        for i, color in enumerate(self.leds):
            if i % 20 == 0 and i > 0:
                print()
            # Simple color approximation
            if color[0] > 200:
                print(f"\033[91m{bar}\033[0m", end="")  # Red
            elif color[1] > 200:
                print(f"\033[92m{bar}\033[0m", end="")  # Green
            elif color[2] > 200:
                print(f"\033[94m{bar}\033[0m", end="")  # Blue
            elif color[0] > 150 and color[1] > 100:
                print(f"\033[93m{bar}\033[0m", end="")  # Yellow/Orange
            elif color[0] > 100 and color[2] > 100:
                print(f"\033[95m{bar}\033[0m", end="")  # Purple
            else:
                print(f"\033[90m{bar}\033[0m", end="")  # Gray/Black
        print()


async def display_flag(strip, colors, name, duration=100):
    """Display a flag for a specified duration"""
    print(f"\n{'='*60}")
    print(f"Displaying: {name}")
    print(f"{'='*60}")

    flag = ColorRanges(strip, colors=colors)

    for step in range(duration):
        await flag.execute(step)

    print()


async def main():
    strip = MockStrip(60)

    # Pride Flag
    pride_colors = [
        (255, 0, 0),      # Red
        (255, 165, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (128, 0, 128),    # Purple
    ]

    # German Flag
    german_colors = [
        (0, 0, 0),        # Black
        (255, 0, 0),      # Red
        (255, 215, 0),    # Gold
    ]

    # Italian Flag
    italian_colors = [
        (0, 146, 70),     # Green
        (255, 255, 255),  # White
        (206, 43, 55),    # Red
    ]

    # French Flag
    french_colors = [
        (0, 85, 164),     # Blue
        (255, 255, 255),  # White
        (239, 65, 53),    # Red
    ]

    flags = [
        (pride_colors, "Pride Flag", 150),
        (german_colors, "German Flag", 100),
        (italian_colors, "Italian Flag", 100),
        (french_colors, "French Flag", 100),
    ]

    print("\n" + "="*60)
    print("FLAG DISPLAY DEMO")
    print("="*60)
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            for colors, name, duration in flags:
                await display_flag(strip, colors, name, duration)
                await asyncio.sleep(1)  # Brief pause between flags
    except KeyboardInterrupt:
        print("\n\nStopping flag display")
        strip.fill((0, 0, 0))
        strip.show()


if __name__ == "__main__":
    asyncio.run(main())

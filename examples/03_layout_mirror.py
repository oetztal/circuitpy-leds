"""
Layout - Mirrored Configuration Example

This example demonstrates how to use the Layout class to create a mirrored
LED setup where setting one LED automatically sets its mirror counterpart.
"""

import asyncio
from circuitpy_leds import Strip
from circuitpy_leds.support.layout import Layout
from circuitpy_leds.shows import Rainbow


class MockStrip(Strip):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.leds = [(0, 0, 0)] * num_leds

    def __len__(self):
        return self.num_leds

    def __setitem__(self, index, value):
        self.leds[index] = value
        print(f"Physical LED {index}: RGB{value}")

    def __getitem__(self, index):
        return self.leds[index]

    def fill(self, color):
        for i in range(self.num_leds):
            self.leds[i] = color

    def show(self):
        pass


async def main():
    # Create a physical strip with 100 LEDs
    physical_strip = MockStrip(100)

    # Create a mirrored layout
    # This creates a logical strip of 50 LEDs that mirrors on both sides
    # Logical LED 0 controls both physical LEDs 0 and 99
    # Logical LED 49 controls both physical LEDs 49 and 50
    mirrored_layout = Layout(
        physical_strip,
        dead=0,
        mirror=True,
        reverse=False
    )

    print(f"Physical strip length: {len(physical_strip)}")
    print(f"Logical (mirrored) length: {len(mirrored_layout)}")
    print("\nSetting colors through mirrored layout:")
    print("Notice how each logical LED sets TWO physical LEDs\n")

    # Demonstrate manual setting
    mirrored_layout[0] = (255, 0, 0)   # Sets physical LEDs 0 and 99
    mirrored_layout[10] = (0, 255, 0)  # Sets physical LEDs 10 and 89
    mirrored_layout[25] = (0, 0, 255)  # Sets physical LEDs 25 and 74

    print("\n" + "="*60)
    print("Now running rainbow on mirrored layout...")
    print("The rainbow will mirror from the center!")
    print("="*60 + "\n")

    # Run rainbow effect on the mirrored layout
    rainbow = Rainbow(mirrored_layout)

    try:
        step = 0
        while step < 500:
            await rainbow.execute(step)
            if step % 100 == 0:
                print(f"Step {step}/500")
            step += 1
    except KeyboardInterrupt:
        pass

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())

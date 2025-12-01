import asyncio
import math

from .. import Strip
from ..support.color import wheel


class Wave:

    def __init__(self, strip: Strip, wave_speed: float = 2.0, decay_rate: float = 0.5, brightness_frequency: float = .4, wavelength: float = 4.0):
        """
        Wave effect that emits from the center with changing brightness and decay towards the ends.

        :param strip: Configuration object
        :param wave_speed: Speed of wave propagation (higher = faster)
        :param decay_rate: Rate of brightness decay towards ends (0-1, higher = faster decay)
        :param brightness_frequency: Frequency of brightness oscillation at the source
        :param wavelength: Wavelength of the wave pattern (higher = longer waves, more spread out)
        """
        self.strip = strip
        self.num_leds = len(strip)
        self.wave_speed = wave_speed
        self.decay_rate = decay_rate
        self.brightness_frequency = brightness_frequency
        self.wavelength = wavelength
        self.time = 0
        self.color_time = 0

    async def execute(self, index: int):
        self.time += 0.05
        self.color_time += 0.05

        # Calculate source brightness using sine wave (oscillates between 0.3 and 1.0)
        source_brightness = 0.65 + 0.35 * math.sin(self.time * self.brightness_frequency * 2 * math.pi)

        self.strip.fill((0, 0, 0))

        for i in range(self.num_leds):
            # Create wave pattern: sine wave propagates outward from center
            wave_position = (i - (self.time * self.wave_speed * 10)) / self.wavelength
            wave_brightness = (math.sin(wave_position) + 1) / 2  # Normalize to 0-1

            # Calculate when this wave element was at the center (emission time)
            # This determines what color it should have
            emission_time = self.color_time - (i / (self.wave_speed * 10))
            color_index = (emission_time * 20) % 255
            pixel_color = wheel(color_index)

            # Apply distance-based decay (exponential decay towards the ends)
            distance_factor = math.exp(-self.decay_rate * i / self.num_leds)

            # Combine source brightness, wave pattern, and distance decay
            final_brightness = source_brightness * wave_brightness * distance_factor

            # Apply brightness to color
            self.strip[i] = tuple(int(c * final_brightness) for c in pixel_color)

        self.strip.show()
        await asyncio.sleep(0)

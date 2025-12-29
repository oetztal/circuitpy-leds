import spidev

from ..config import Config
from ..support.color import grayscale_correction
from .. import Strip

# SPDX-License-Identifier: Apache-2.0
#
# Portions of this code are derived from the 102shows project:
# https://github.com/Yottabits/102shows
# Original code is licensed under GPL-2.0
#
# NOTE: The inclusion of GPL-2.0 derived code in an Apache-2.0 project
# may create license compatibility issues. Please review and either:
# - Rewrite the affected functions independently, or
# - Consult with legal counsel regarding license compatibility


class APA102(Strip):

    def __init__(self, config: Config):
        self.num_leds = config.num_leds
        self._global_brightness = 0.3
        self.spi = spidev.SpiDev()  # Init the SPI device
        self.spi.open(0, 1)  # Open SPI port 0, slave device (CS)  1
        max_clock_speed_hz = 4000000
        self.spi.max_speed_hz = max_clock_speed_hz  # should not be higher than 8000000

        self.led_colors = [(0.0, 0.0, 0.0)] * self.num_leds
        self.leds = [self.led_prefix(self._global_brightness), 0, 0, 0] * self.num_leds  # 4 bytes per LED

    @classmethod
    def led_prefix(cls, brightness: float) -> int:
        """
        generates the first byte of a 4-byte SPI message to a single APA102 module

        :param brightness: float from 0.0 (off) to 1.0 (full brightness)
        :return: the brightness byte
        """

        # map 0 - 1 brightness parameter to 0 - 31 integer as used in the APA102 prefix byte
        brightness_byte = grayscale_correction(brightness, max_in=1, max_out=31)

        # structure of the prefix byte: (1 1 1 b4 b3 b2 b1 b0)
        #    - the first three ones are fixed
        #    - (b4, b3, b2, b1, b0) is the binary brightness value (5 bit <=> 32 steps - from 0 to 31)
        prefix_byte = (brightness_byte & 0b00011111) | 0b11100000

        return prefix_byte

    @staticmethod
    def spi_start_frame() -> list:
        """
        To start a transmission, one must send 32 empty bits

        :return: The 32-bit start frame to be sent at the beginning of a transmission
        """
        return [0, 0, 0, 0]  # Start frame, 4 empty bytes <=> 32 zero bits

    def show(self) -> None:
        """sends the buffered color and brightness values to the strip"""
        for i in range(self.num_leds):
            real_index = i * 4
            self.leds[real_index] = self.led_prefix(self._global_brightness)
            color_tuple = self.led_colors[i]
            self.leds[real_index + 1] = int(color_tuple[2])
            self.leds[real_index + 2] = int(color_tuple[1])
            self.leds[real_index + 3] = int(color_tuple[0])

        self.spi.xfer2(self.spi_start_frame())
        self.spi.xfer2(self.leds.copy())  # SPI takes up to 4096 Integers. So we are fine for up to 1024 LEDs.
        self.spi.xfer(self.spi_end_frame(self.num_leds))

    @staticmethod
    def spi_end_frame(num_leds) -> list:
        """\
        As explained above, dummy data must be sent after the last real color information so that all of the data
        can reach its destination down the line.
        The delay is not as bad as with the human example above. It is only 1/2 bit per LED. This is because the
        SPI clock line needs to be inverted.

        Say a bit is ready on the SPI data line. The sender communicates this by toggling the clock line. The bit
        is read by the LED, and immediately forwarded to the output data line. When the clock goes down again
        on the input side, the LED will toggle the clock up on the output to tell the next LED that the bit is ready.

        After one LED the clock is inverted, and after two LEDs it is in sync again, but one cycle behind. Therefore,
        for every two LEDs, one bit of delay gets accumulated. For 300 LEDs, 150 additional bits must be fed to
        the input of LED one so that the data can reach the last LED. In this implementation we add a few more zero
        bytes at the end, just to be sure.

        Ultimately, we need to send additional *num_leds/2* arbitrary data bits, in order to trigger *num_leds/2*
        additional clock changes. This driver sends zeroes, which has the benefit of getting LED one partially or
        fully ready for the next update to the strip. An optimized version of the driver could omit the
        :py:func:`spi_start_frame` method if enough zeroes have been sent as part of :py:func:`spi_end_frame`.

        :return: The end frame to be sent at the end of each SPI transmission
        """
        return [0x00] * ((num_leds + 15) // 16)  # Round up num_leds/2 bits (or num_leds/16 bytes)


    def __setitem__(self, index, value):
        if index < 0:
            return  # Pixel is invisible, so ignore
        if index >= self.num_leds:
            return  # again, invisible

        self.led_colors[index] = value


    def __getitem__(self, index):
        return self.led_colors[index]

    def __len__(self):
        return self.num_leds

    def fill(self, color):
        for i in range(self.num_leds):
            self[i] = color
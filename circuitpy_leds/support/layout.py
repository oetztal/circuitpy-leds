
# from adafruit_pixelbuf import ColorUnion
from circuitpy_leds import Strip

class Layout(Strip):

    def __init__(self, pixels: Strip, dead=102, mirror=True, reverse=False):
        self.strip = pixels
        self.dead = dead
        self.mirror = mirror
        self.reverse = reverse

        self._turn_off_dead_leds()

    def __len__(self):
        return int((len(self.strip) - abs(self.dead)) / (2 if self.mirror else 1))

    def __setitem__(self, index: int | slice, val):
        index = self.real_index(index)
        self.strip[index] = val
        if self.mirror:
            self.strip[len(self.strip) - index - 1] = val

    def __getitem__(self, index: int):
        return self.strip[self.real_index(index)]

    def real_index(self, index: int | slice) -> int | slice:
        if not 0 <= index < len(self):
            raise IndexError("Index out of range")
        if not self.mirror:
            if self.dead > 0:
                index += self.dead
        else:
            if self.dead < 0:
                index += int(-self.dead / 2)
        if self.reverse:
            index = len(self) - index - 1
        return index

    def fill(self, color):
        self.strip.fill(color)

    def show(self):
        self.strip.show()

    def _turn_off_dead_leds(self):
        """Clear (turn off) the dead LEDs."""
        if self.dead == 0:
            return

        black = (0, 0, 0)

        if self.mirror:
            # For mirrored layouts, dead LEDs are in the middle
            if self.dead > 0:
                # Dead LEDs in the middle between mirrored sections
                # Left side: 0 to (len(self)-1), Dead middle, Right side (mirrored)
                left_side_end = len(self)
                dead_start = left_side_end
                dead_end = dead_start + self.dead
                for i in range(dead_start, dead_end):
                    self.strip[i] = black
            else:
                # Negative dead with mirror: half the number of dead LEDs at the beginning and at end
                half_dead = int(abs(self.dead / 2))
                for i in range(half_dead):
                    self.strip[i] = black
                    self.strip[len(self)-i] = black
        else:
            # For non-mirrored layouts
            if self.dead > 0:
                # Dead LEDs at the end of the strip
                start = len(self.strip) - self.dead
                for i in range(start, len(self.strip)):
                    self.strip[i] = black
            else:
                # Dead LEDs at the beginning of the strip (negative dead)
                for i in range(abs(self.dead)):
                    self.strip[i] = black


# from adafruit_pixelbuf import ColorUnion
from circuitpy_leds import Strip

class Layout(Strip):

    def __init__(self, pixels: Strip, dead=102, mirror=True, reverse=False):
        self.strip = pixels
        self.dead = dead
        self.mirror = mirror
        self.reverse = reverse

        # Clear dead LEDs (turn them off)
        self._clear_dead_leds()

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
        if self.dead < 0:
            index += -self.dead
        if self.reverse:
            index = len(self) - index - 1
        return index

    def fill(self, color):
        self.strip.fill(color)

    def show(self):
        self.strip.show()

    def _clear_dead_leds(self):
        """Clear (turn off) the dead LEDs."""
        if self.dead == 0:
            return

        black = (0, 0, 0)

        if self.dead > 0:
            # Dead LEDs at the end of the strip
            start = len(self.strip) - self.dead
            for i in range(start, len(self.strip)):
                self.strip[i] = black
        else:
            # Dead LEDs at the beginning of the strip (negative dead)
            for i in range(abs(self.dead)):
                self.strip[i] = black

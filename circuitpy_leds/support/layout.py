
# from adafruit_pixelbuf import ColorUnion
from circuitpy_leds import Strip

class Layout(Strip):

    def __init__(self, pixels: Strip, dead=102, mirror=True):
        self.strip = pixels
        self.dead = dead
        self.mirror = mirror

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
        return index

    def fill(self, color):
        self.strip.fill(color)

    def show(self):
        self.strip.show()

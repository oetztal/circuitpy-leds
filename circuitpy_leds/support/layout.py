from typing import Union, Sequence

from adafruit_pixelbuf import ColorUnion
from circuitpy_leds import Strip

class Layout(Strip):

    def __init__(self, pixels: Strip, dead=102, mirror=True):
        self.strip = pixels
        self.dead = dead
        self.mirror = mirror

    def __len__(self):
        return int((len(self.strip) - abs(self.dead)) / (2 if self.mirror else 1))

    def __setitem__(self, index: Union[int, slice], val: Union[ColorUnion, Sequence[ColorUnion]]):
        if not 0 <= index < len(self):
            raise IndexError("Index out of range")
        if self.dead < 0:
            index += -self.dead
        self.strip[index] = val
        if self.mirror:
            self.strip[len(self.strip) - index - 1] = val

    def show(self):
        self.strip.show()

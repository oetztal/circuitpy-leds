
# from adafruit_pixelbuf import ColorUnion
from circuitpy_leds import Strip

class Layout(Strip):
    """

    ## plain

    n = <number of leds> - 1

    plain:   0**********n
    reverse: n**********0

    ## mirrored

    mirrored:          0****mm****0
    mirrored, reverse: m****00****m

    m = (<number of leds> / 2) - 1
    
    ## using dead LEDs

    o = <number of leds> - 1 - <dead leds>

    dead > 0:          ---0******o
    dead > 0, reverse: ---o******0
    dead < 0:          0******o---
    dead < 0, reverse: 0******o---

    ### mirrored

    p = (<number of leds> - abs(<dead leds>)) / 2 - 1

    dead > 0, mirrored:          0**p----p**0 TESTED
    dead > 0, mirrored, reverse: p**0----0**p
    dead < 0, mirrored:          --0**pp**0-- TESTED
    dead < 0, mirrored, reverse: --p**00**p--


    """

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
        # Apply reverse first (within logical layout space)
        if self.reverse:
            index = len(self) - index - 1
        # Then apply dead LED offset to get physical strip index
        if not self.mirror:
            if self.dead > 0:
                index += self.dead
        else:
            if self.dead < 0:
                index += int(-self.dead / 2)
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
                # Dead LEDs at the beginning of the strip
                for i in range(abs(self.dead)):
                    self.strip[i] = black
            else:
                # Dead LEDs at the end of the strip
                start = len(self.strip) - self.dead
                for i in range(start, len(self.strip)):
                    self.strip[i] = black

    def __repr__(self):
        state = []

        if self.mirror:
            state.append("mirror")

        if self.reverse:
            state.append("reverse")

        if self.dead:
            state.append(f"dead={self.dead}")

        if not state:
            state.append("default")
        return f"<Layout {', '.join(state)}>"


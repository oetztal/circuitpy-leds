
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

    dead > 0, mirrored:          0**p----p**0
    dead > 0, mirrored, reverse: p**0----0**p
    dead < 0, mirrored:          --0**pp**0--
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

        if self.mirror:
            self._turn_off_mirrored_dead_leds()
        else:
            self._turn_off_plain_dead_leds()

    def _turn_off_mirrored_dead_leds(self):
        """Turn off dead LEDs for mirrored layout configurations."""
        if self.dead > 0:
            self._turn_off_middle_leds()
        else:
            self._turn_off_edge_leds()

    def _turn_off_plain_dead_leds(self):
        """Turn off dead LEDs for non-mirrored layout configurations."""
        if self.dead > 0:
            self._turn_off_beginning_leds()
        else:
            self._turn_off_end_leds()

    def _turn_off_middle_leds(self):
        """
        Turn off LEDs in the middle (positive dead, mirrored).

        Layout: 0**p----p**0
        Dead LEDs are in the center between mirrored sections.
        """
        left_side_end = len(self)
        dead_start = left_side_end
        dead_end = dead_start + self.dead
        self._set_range_to_black(dead_start, dead_end)

    def _turn_off_edge_leds(self):
        """
        Turn off LEDs at both edges (negative dead, mirrored).

        Layout: --0**pp**0--
        Half the dead LEDs at beginning, half at end.
        """
        half_dead = int(abs(self.dead / 2))
        for i in range(half_dead):
            self.strip[i] = (0, 0, 0)
            self.strip[len(self) - i] = (0, 0, 0)

    def _turn_off_beginning_leds(self):
        """
        Turn off LEDs at the beginning (positive dead, non-mirrored).

        Layout: ---0******o
        Dead LEDs are at the start of the strip.
        """
        self._set_range_to_black(0, abs(self.dead))

    def _turn_off_end_leds(self):
        """
        Turn off LEDs at the end (negative dead, non-mirrored).

        Layout: 0******o---
        Dead LEDs are at the end of the strip.
        """
        start = len(self.strip) + self.dead  # dead is negative
        self._set_range_to_black(start, len(self.strip))

    def _set_range_to_black(self, start, end):
        """Set a range of LEDs to black (off)."""
        black = (0, 0, 0)
        for i in range(start, end):
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


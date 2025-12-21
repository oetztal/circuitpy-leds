from .color_ranges import ColorRanges
from .color_run import ColorRun
from .jump import Jump
from .morse_code import MorseCode
from .rainbow import Rainbow
from .solid import Solid
from .two_color_blend import TwoColorBlend
from .starlight import Starlight
from .theater_chase import TheaterChase
from .wave import Wave

SHOW_MAP = {
    "solid": Solid,
    "two_color_blend": TwoColorBlend,
    "rainbow": Rainbow,
    "jump": Jump,
    "color_run": ColorRun,
    "starlight": Starlight,
    "theater_chase": TheaterChase,
    "wave": Wave,
    "morse_code": MorseCode,
    "color_ranges": ColorRanges,
}
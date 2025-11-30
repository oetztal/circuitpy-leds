from .color_run import ColorRun
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
    "color_run": ColorRun,
    "starlight": Starlight,
    "theater_chase": TheaterChase,
    "wave": Wave,
}
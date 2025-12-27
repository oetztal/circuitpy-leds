import asyncio

import board
import touchio
from neopixel import NeoPixel

from . import Control
from ..config import Config
from ..shows import Solid, ColorRanges, ColorRun, MorseCode, Rainbow, Starlight, TwoColorBlend, TheaterChase, Wave
from ..shows.jump import Jump
from ..support.layout import Layout


SHOWS = [
    (lambda strip, args: Solid(strip, *args), [
        [(255, 170, 120)],
        [(255, 255, 255)],
        [(255, 0, 0)],
        [(255, 127, 0)],
        [(255, 255, 0)],
        [(0, 255, 0)],
        [(0, 255, 255)],
        [(0, 127, 255)],
        [(0, 0, 255)],
        [(255, 0, 255)],
    ]),
    (lambda strip, args: ColorRanges(strip, *args), [
        [[(0, 0, 255), (255, 255, 0)]],
        [[(255,0,0), (255,255,255), (0,255,0)]],
        [[(170, 21, 27), (241, 191, 0), (170, 21, 27)], [25, 75]]
    ]),
    (lambda strip, args: TwoColorBlend(strip, *args), [
        [(0, 0, 255), (255, 0, 0)],
        [(0, 255, 0), (255, 0, 0)],
        [(0, 255, 0), (0, 0, 255)],
    ]),
    (lambda strip, args: ColorRun(strip), []),
    (lambda strip, args: Jump(strip, *args), []),
    (lambda strip, args: Rainbow(strip), []),
    (lambda strip, args: Wave(strip),[]),
    (lambda strip, args: Starlight(strip, *args), [
        [0.1, 0.0, 0.25],
        [0.02, 5.0, 1.0],
    ]),
    (lambda strip, args: TheaterChase(strip, *args), [[21], [42], [84]]),
    (lambda strip, args: MorseCode(strip, *args), [["foo bar baz"], ["gutes neues"]])
]

LAYOUTS = [
    lambda pixels: Layout(pixels, 0, False),
    lambda pixels: Layout(pixels, 0, False, True),
    lambda pixels: Layout(pixels, 0, True),
    lambda pixels: Layout(pixels, 0, True, True),
    lambda pixels: Layout(pixels, 100, True),
    lambda pixels: Layout(pixels, 100, True, True),
]

brightness = [0.05, 0.1, 0.5]


async def control_touch(effect: Control, config: Config, pixels: NeoPixel):
    touch_threshold = config.touch_threshold

    touch_show = touchio.TouchIn(board.A2)
    touch_show.threshold = touch_threshold
    touch_mode = touchio.TouchIn(board.TX)
    touch_mode.threshold = touch_threshold
    touch_layout = touchio.TouchIn(board.SDA)
    touch_layout.threshold = touch_threshold

    show_index = 0
    mode_index_map = [0] * len(SHOWS)
    layout_index_map = [0] * len(SHOWS)
    brightness_index = 0
    updated = True
    pixels.brightness = brightness[brightness_index]

    while True:
        if touch_show.value:
            print("-- show touched", touch_show.value, touch_show.raw_value, touch_show.threshold)
            show_index += 1
            show_index = show_index % len(SHOWS)
            updated = True

        if touch_mode.value:
            print("-- mode touched", touch_mode.value, touch_mode.raw_value, touch_mode.threshold)
            show_data = SHOWS[show_index]
            mode_index = mode_index_map[show_index]
            mode_index += 1
            mode_index = mode_index % len(show_data[1]) if show_data[1] else 0
            mode_index_map[show_index] = mode_index
            updated = True

        if touch_layout.value:
            print("-- layout touched", touch_layout.value, touch_layout.raw_value, touch_layout.threshold)
            layout_index = layout_index_map[show_index]
            layout_index += 1
            layout_index = layout_index % len(LAYOUTS)
            layout_index_map[show_index] = layout_index
            updated = True

        if updated:
            show_data = SHOWS[show_index]
            mode_index = mode_index_map[show_index]
            layout_index = layout_index_map[show_index]
            show_factory = show_data[0]
            show_args = show_data[1][mode_index] if show_data[1] else []
            layout = LAYOUTS[layout_index % len(LAYOUTS)](pixels)
            print(f"*** show: {show_index}, args: {show_args}, layout: {layout}")
            effect.current_show = show_factory(layout, show_args)

            await asyncio.sleep(0.5)
            updated = False

        await asyncio.sleep(0.1)

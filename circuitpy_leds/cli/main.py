import asyncio

from shows import ColorRanges
from ..support.layout import Layout
from ..shows import ColorRun, Solid, Rainbow, TheaterChase, Jump, Starlight, MorseCode, Wave
from ..config import Config
from ..control import Control
from ..driver.apa102 import APA102

async def run_effect(control: Control):
    index = 0
    while True:
        await control.execute(index)
        index += 1

async def async_main(config):
    strip = APA102(config)
    # strip = Layout(strip, 102, True)
    sides = Layout(strip, 102, True)

    control = Control(strip)
    # control.current_show = Rainbow(strip)
    # control.current_show = Solid(strip, (255, 0, 0))
    # control.current_show = ColorRun(strip)
    # control.current_show = TheaterChase(strip)
    # control.current_show = Jump(sides)
    # control.current_show = Starlight(strip, 0.1, 0.0, 0.25)
    # control.current_show = Wave(Layout(strip,0, True, True))
    # control.current_show = MorseCode(strip, message="foo bar baz qux quux", speed=0.5, sleep_time=0.025)
    control.current_show = ColorRanges(strip, colors=[(0,0,255), (255,255,0)])
    led_task = asyncio.create_task(run_effect(control))

    await asyncio.gather(led_task)



def main():
    config = type('obj', (object,), {'num_leds' : 300})
    asyncio.run(async_main(config))

import asyncio

from ..support.layout import Layout
from ..shows import ColorRun, Solid, Rainbow, TheaterChase, Jump
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
    strip = Layout(strip, 102, True)

    control = Control(strip)
    # control.current_show = Rainbow(strip)
    # control.current_show = Solid(strip, (255, 0, 0))
    # control.current_show = ColorRun(strip)
    control.current_show = TheaterChase(strip)
    control.current_show = Jump(strip)

    led_task = asyncio.create_task(run_effect(control))

    await asyncio.gather(led_task)



def main():
    config = type('obj', (object,), {'num_leds' : 300})
    asyncio.run(async_main(config))

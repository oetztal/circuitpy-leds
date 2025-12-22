import asyncio

from ..config import Config
from ..control import Control
from ..control.async_mqtt import AsyncMQTTControl
from ..driver.apa102 import APA102


async def run_effect(control: Control):
    index = 0
    while True:
        await control.execute(index)
        index += 1


async def async_main(config):
    strip = APA102(config)

    control = Control(strip)

    led_task = asyncio.create_task(run_effect(control))

    mqtt_control = AsyncMQTTControl(control, strip, config)
    mqtt_task = asyncio.create_task(mqtt_control.run())

    await asyncio.gather(led_task, mqtt_task)


def main():
    asyncio.run(async_main(Config()))

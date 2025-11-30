import asyncio

from neopixel import NeoPixel

from circuitpy_leds.config import Config
from circuitpy_leds.wifi import wifi_connect
from circuitpy_leds.control import Control
from circuitpy_leds.control.touch import control_touch

async def run_effect(pixels, control: Control):
    index = 0
    while True:
        await control.execute(index)
        index += 1


async def main():
    print("starting main")
    config = Config()
    # socket_pool = wifi_connect(config)

    # mqtt = MQTTClient(socket_pool, config)
    # mqtt.connect()
    # mqtt.subscribe(config.mqtt_prefix)

    pixels = NeoPixel(config.output_pin, config.num_leds, auto_write=False, brightness=0.1)

    control = Control(pixels)

    led_task = asyncio.create_task(run_effect(pixels, control))
    # control_task = asyncio.create_task(control_mqtt(effect, mqtt, config, pixels))
    # control_task = asyncio.create_task(control_tcp(control, config, pixels))
    control_task = asyncio.create_task(control_touch(control, config, pixels))

    await asyncio.gather(led_task, control_task)


asyncio.run(main())

import asyncio

from neopixel import NeoPixel

from circuitpy_leds.config import Config
from circuitpy_leds.control import Control
from circuitpy_leds.control.touch import control_touch


async def run_effect(control: Control):
    index = 0
    while True:
        await control.execute(index)
        index += 1


async def main():
    print("starting main")
    config = Config()

    pixels = NeoPixel(config.output_pin, config.num_leds, auto_write=False, brightness=0.1)

    control = Control(pixels)

    # Create task list
    tasks = [
        asyncio.create_task(run_effect(control)),
        asyncio.create_task(control_touch(control, config, pixels))
    ]

    # Add MQTT control if configured
    if config.mqtt_host:
        print(f"MQTT enabled - connecting to {config.mqtt_host}")

        from circuitpy_leds.circuitpy.wifi import wifi_connect
        socket_pool = wifi_connect(config)
        print("WiFi connected")

        from circuitpy_leds.circuitpy.mqtt import MQTTClient
        mqtt = MQTTClient(socket_pool, config)
        mqtt.connect()
        mqtt.subscribe(config.mqtt_prefix)

        from circuitpy_leds.control.mqtt import control_mqtt
        control_task = asyncio.create_task(control_mqtt(control, mqtt, config, pixels))
    else:
        control_task = asyncio.create_task(control_touch(control, config, pixels))
        print("MQTT disabled - no MQTT_HOST configured")

    tasks.append(control_task)

    await asyncio.gather(*tasks)


asyncio.run(main())

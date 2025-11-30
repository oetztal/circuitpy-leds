import asyncio
import json

from neopixel import NeoPixel

from ..config import Config
from ..mqtt import MQTTClient
from . import Control
from ..shows import SHOW_MAP


async def control_mqtt(effect: Control, mqtt: MQTTClient, config: Config, pixels: NeoPixel):

    while True:
        mqtt.loop()

        message = mqtt.pop_message()
        if message:
            message_json = {}
            try:
                message_json = json.loads(message)
            except ValueError as e:
                print(f"ValueError: {e}")

            if "effect" in message_json:
                effect_name = message_json["effect"]
                args = message_json.get("args", [])
                args = [config] + args
                kwargs = message_json.get("kwargs", {})
                print(f"Effect: {effect_name} args: {args} kwargs: {kwargs}")
                try:
                    effect.current_show = SHOW_MAP[effect_name](*args, **kwargs)
                except TypeError as e:
                    print(f"TypeError: {e}")

            if "brightness" in message_json:
                pixels.brightness = message_json["brightness"]

        await asyncio.sleep(5)
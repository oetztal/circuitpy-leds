import asyncio

from neopixel import NeoPixel

from ..shows import SHOW_MAP
from ..config import Config
from . import Control


class TcpServer:

    def __init__(self):
        self.messages = []
        self.server = None

    async def start(self):
        print("Starting TCP server on port 12345")
        self.server = await asyncio.start_server(self.on_connect, "0.0.0.0", 12345)
        print("Started TCP server")

    async def on_connect(self, client_reader, client_writer):
        print("Client connected")

        while True:
            data = await client_reader.readline()
            if not data:
                print("Client disconnected")
                break
            print("Received:", data)
            message = data.decode()
            self.messages.append(message)

            client_writer.write(f"received {message}".encode())
            await client_writer.drain()


async def control_tcp(control: Control, config: Config, pixels: NeoPixel):
    server = TcpServer()

    await server.start()

    while True:
        if server.messages:
            message = server.messages.pop(0)
            print("Processing message:", message)
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
                    control.current_show = SHOW_MAP[effect_name](*args, **kwargs)
                except TypeError as e:
                    print(f"TypeError: {e}")

            if "brightness" in message_json:
                pixels.brightness = message_json["brightness"]
        await asyncio.sleep(1)

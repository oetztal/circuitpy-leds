import asyncio
import json
import time

try:
    import paho.mqtt.client as mqtt
except ImportError:
    mqtt = None

from .. import Strip
from ..config import Config
from ..shows import SHOW_MAP
from ..support.layout import Layout
from . import Control


class AsyncMQTTControl:
    """
    Async MQTT control handler with event-driven message processing.

    Features:
    - Event-driven message handling via async queue
    - Auto-reconnect with exponential backoff
    - Status publishing
    - Show switching and brightness control
    - Graceful error handling
    """

    def __init__(self, control: Control, pixels: Strip, config: Config, mqtt_client=None):
        """
        Initialize async MQTT control.

        :param control: Control instance managing current show
        :param pixels: LED strip/NeoPixel instance
        :param config: Configuration object
        :param mqtt_client: Optional MQTT client (for testing)
        """
        self.control = control
        self.pixels = pixels
        self.config = config
        self.mqtt_client = mqtt_client
        self.message_queue = asyncio.Queue()
        self.running = False
        self.connected = False
        self.start_time = time.monotonic()
        self.current_show_name = None
        self.loop = None  # Event loop reference for thread-safe scheduling

    async def run(self):
        """
        Main entry point - runs all MQTT tasks concurrently.
        """
        self.running = True
        self.loop = asyncio.get_event_loop()  # Store loop reference for callbacks

        try:
            # Run all tasks concurrently
            await asyncio.gather(
                self._connection_manager(),
                self._message_processor(),
                self._status_publisher(),
                self._keepalive_loop()
            )
        except Exception as e:
            print(f"MQTT error: {e}")
        finally:
            self.running = False
            # Cleanup Paho client
            if self.mqtt_client:
                try:
                    self.mqtt_client.loop_stop()
                    self.mqtt_client.disconnect()
                except Exception as e:
                    print(f"Error disconnecting MQTT: {e}")

    async def _connection_manager(self):
        """
        Manage MQTT connection with exponential backoff retry.
        """
        retry_delay = self.config.mqtt_reconnect_delay
        max_delay = 60

        while self.running:
            try:
                if not self.connected:
                    await self._connect()
                    retry_delay = self.config.mqtt_reconnect_delay  # Reset delay on success

                # Wait before checking again
                await asyncio.sleep(10)

            except Exception as e:
                print(f"MQTT connection failed: {e}")
                self.connected = False
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)

    async def _connect(self):
        """
        Establish MQTT connection and subscribe to command topics.
        """
        if self.mqtt_client is None:
            if mqtt is None:
                print("Paho MQTT client not available")
                return

            # Create Paho MQTT client
            client_id = self.config.mqtt_client_id or f"circuitpy-leds-{id(self)}"
            self.mqtt_client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

            # Set callbacks
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_message = self._on_message
            self.mqtt_client.on_disconnect = self._on_disconnect

        # Connect to broker
        print(f"Connecting to MQTT broker: {self.config.mqtt_host}:{self.config.mqtt_port}")
        self.mqtt_client.connect(self.config.mqtt_host, self.config.mqtt_port, keepalive=60)

        # Start network loop in background thread
        self.mqtt_client.loop_start()

        self.connected = True
        print(f"MQTT connection initiated to {self.config.mqtt_host}")

    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback when connection is established.

        This runs in Paho's background thread, so we need thread-safe scheduling.
        """
        if rc == 0:
            print("MQTT connected successfully")

            # Subscribe to all command topics
            command_base = f"{self.config.mqtt_prefix}/led/command/#"
            client.subscribe(command_base)
            print(f"Subscribed to {command_base}")

            # Publish initial status (thread-safe)
            if self.loop:
                self.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self._publish_status())
                )
        else:
            print(f"MQTT connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """
        Callback when disconnected from broker.
        """
        print(f"MQTT disconnected with code {rc}")
        self.connected = False

    def _on_message(self, client, userdata, message):
        """
        MQTT message callback - queues messages for async processing.

        This is called from the MQTT client thread, so we just queue
        the message for processing in the async loop.

        Paho callback signature: (client, userdata, message)
        message.topic: str
        message.payload: bytes
        """
        # Decode payload from bytes to string
        try:
            payload = message.payload.decode('utf-8')
            topic = message.topic
        except Exception as e:
            print(f"Error decoding message: {e}")
            return

        # Queue message for async processing (thread-safe)
        if self.loop:
            try:
                self.loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(self.message_queue.put((topic, payload)))
                )
            except Exception as e:
                print(f"Error queuing message: {e}")

    async def _message_processor(self):
        """
        Process messages from the queue as they arrive.
        """
        while self.running:
            try:
                # Wait for message from queue
                topic, message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                await self._handle_message(topic, message)

            except asyncio.TimeoutError:
                # No message, continue
                continue
            except Exception as e:
                print(f"Message processing error: {e}")

    async def _handle_message(self, topic: str, payload: str):
        """
        Process a single MQTT message based on topic.

        :param topic: MQTT topic
        :param payload: Message payload (string)
        """
        try:
            # Extract command from topic
            # Format: {prefix}/led/command/{command}
            parts = topic.split('/')
            if len(parts) < 4 or parts[-2] != 'command':
                print(f"Invalid topic format: {topic}")
                return

            command = parts[-1]

            # Route to appropriate handler
            if command == 'show':
                await self._handle_show_command(payload)
            elif command == 'brightness':
                await self._handle_brightness_command(payload)
            elif command == 'power':
                await self._handle_power_command(payload)
            elif command == 'param':
                await self._handle_param_command(payload)
            else:
                print(f"Unknown command: {command}")

        except Exception as e:
            print(f"Error handling message on {topic}: {e}")

    async def _handle_show_command(self, payload: str):
        """
        Handle show change command.

        Payload format (JSON):
        {
          "show": "solid",
          "args": [[255, 0, 0]],
          "kwargs": {},
          "layout": {
            "dead": 0,
            "mirror": false,
            "reverse": false
          }
        }

        The layout parameter is optional. If specified, it wraps the pixel strip
        with a Layout instance before creating the show.
        """
        try:
            message = json.loads(payload)
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Invalid JSON: {e}")
            return

        show_name = message.get('show')
        if not show_name:
            print("No show specified")
            return

        if show_name not in SHOW_MAP:
            print(f"Unknown show: {show_name}")
            return

        # Parse args and kwargs
        # Note: JSON arrays become Python lists, but most shows accept lists as colors
        # ColorRanges specifically expects list[list[int]] and validates/converts internally
        args = message.get('args', [])
        kwargs = message.get('kwargs', {})

        # Handle layout configuration
        pixels = self.pixels
        layout_config = message.get('layout')
        if layout_config:
            dead = layout_config.get('dead', 0)
            mirror = layout_config.get('mirror', False)
            reverse = layout_config.get('reverse', False)
            pixels = Layout(self.pixels, dead=dead, mirror=mirror, reverse=reverse)
            print(f"Using layout: dead={dead}, mirror={mirror}, reverse={reverse}")

        # Instantiate and switch show
        try:
            print(f"show {show_name} args: {args} kwargs: {kwargs}")
            new_show = SHOW_MAP[show_name](pixels, *args, **kwargs)
            self.control.current_show = new_show
            self.current_show_name = show_name
            print(f"Switched to show: {show_name}")

            # Publish updated status
            await self._publish_status()

        except TypeError as e:
            print(f"Failed to create show {show_name}: {e}")
        except Exception as e:
            print(f"Error creating show: {e}")

    async def _handle_brightness_command(self, payload: str):
        """
        Handle brightness change command.

        Payload can be:
        - Simple float: "0.5"
        - JSON: {"brightness": 0.5}
        """
        try:
            # Try parsing as JSON first
            try:
                message = json.loads(payload)
                if isinstance(message, dict):
                    brightness = message.get('brightness')
                else:
                    # message is already a number
                    brightness = message
            except (ValueError, json.JSONDecodeError):
                # Try parsing as simple float
                brightness = float(payload)

            if brightness is None:
                print("No brightness value specified")
                return

            # Clamp to valid range
            brightness = max(0.0, min(1.0, float(brightness)))

            self.pixels.brightness = brightness
            print(f"Brightness set to: {brightness}")

            # Publish updated status
            await self._publish_status()

        except (ValueError, TypeError) as e:
            print(f"Invalid brightness value: {e}")

    async def _handle_power_command(self, payload: str):
        """
        Handle power on/off command.

        Payload can be:
        - Simple string: "on" / "off"
        - JSON: {"power": "on"}
        """
        try:
            # Try parsing as JSON first
            try:
                message = json.loads(payload)
                power = message.get('power')
            except (ValueError, json.JSONDecodeError):
                # Use payload directly
                power = payload.strip().lower()

            if power == 'on':
                # Restore previous brightness or set to default
                self.pixels.brightness = 0.1
                print("LEDs powered on")
            elif power == 'off':
                # Set brightness to 0
                self.pixels.brightness = 0.0
                print("LEDs powered off")
            else:
                print(f"Invalid power command: {power}")
                return

            # Publish updated status
            await self._publish_status()

        except Exception as e:
            print(f"Error handling power command: {e}")

    async def _handle_param_command(self, payload: str):
        """
        Handle parameter update command (future enhancement).

        For now, this just re-instantiates the show with new parameters.
        """
        print("Parameter updates not yet implemented")
        # TODO: Implement in Phase 3

    async def _status_publisher(self):
        """
        Periodically publish status to MQTT.
        """
        mqtt_status_interval = 30 # self.config.mqtt_status_interval
        while self.running:
            try:
                print(self.config)
                await asyncio.sleep(mqtt_status_interval)

                if self.connected:
                    await self._publish_status()

            except Exception as e:
                print(f"Status publishing error: {e}")

    async def _publish_status(self):
        """
        Publish current status to MQTT status topic.
        """
        if not self.connected or self.mqtt_client is None:
            return

        try:
            uptime = int(time.monotonic() - self.start_time)

            status = {
                "show": self.current_show_name or "none",
                "brightness": self.pixels.brightness,
                "power": "on" if self.pixels.brightness > 0 else "off",
                "uptime": uptime,
            }

            status_json = json.dumps(status)
            status_topic = f"{self.config.mqtt_prefix}/led/status/state"

            self.mqtt_client.publish(status_topic, status_json)
            print(f"Published status: {status_json}")

        except Exception as e:
            print(f"Failed to publish status: {e}")

    async def _keepalive_loop(self):
        """
        Monitor MQTT connection health.

        Note: Paho's loop_start() handles network I/O in a background thread,
        so we just monitor connection state here.
        """
        while self.running:
            try:
                # Just sleep - Paho's loop_start() handles network I/O
                await asyncio.sleep(1)

            except Exception as e:
                print(f"MQTT keepalive error: {e}")
                self.connected = False
                await asyncio.sleep(1)

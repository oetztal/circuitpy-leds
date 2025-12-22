import os

import board


class Config:

    @property
    def wifi_ssid(self) -> str | None:
        return os.getenv("WIFI_SSID")

    @property
    def wifi_password(self) -> str | None:
        return os.getenv("WIFI_PASSWORD")

    @property
    def mqtt_host(self) -> str | None:
        return os.getenv("MQTT_HOST")

    @property
    def mqtt_port(self) -> int:
        return int(os.getenv("MQTT_PORT", "1883"))

    @property
    def mqtt_client_id(self) -> str | None:
        return os.getenv("MQTT_CLIENT_ID")

    @property
    def mqtt_prefix(self) -> str:
        return os.getenv("MQTT_PREFIX", "ledstrip")

    @property
    def mqtt_status_interval(self) -> int:
        """Interval in seconds between status publications"""
        return int(os.getenv("MQTT_STATUS_INTERVAL", "30"))

    @property
    def mqtt_reconnect_delay(self) -> int:
        """Initial delay in seconds before reconnecting after connection failure"""
        return int(os.getenv("MQTT_RECONNECT_DELAY", "5"))

    @property
    def mqtt_command_topic(self) -> str:
        """Base topic for receiving commands"""
        return f"{self.mqtt_prefix}/led/command"

    @property
    def mqtt_status_topic(self) -> str:
        """Base topic for publishing status"""
        return f"{self.mqtt_prefix}/led/status"

    @property
    def output_pin(self) -> board.Pin | None:
        output_pin_name = os.getenv("OUTPUT_PIN", "NEOPIXEL")
        output_pin = None
        for key in dir(board):
            if key == output_pin_name:
                output_pin = getattr(board, key)
                break
        return output_pin

    @property
    def num_leds(self):
        return int(os.getenv("NUM_LEDS", "1"))

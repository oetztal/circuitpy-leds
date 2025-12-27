import os

import board


class Config:

    @property
    def brightness(self) -> float | None:
        return float(os.getenv("BRIGHTNESS", "0.1"))

    @property
    def dead_leds(self) -> int | None:
        return int(os.getenv("DEAD_LEDS", "100"))

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
    def touch_threshold(self) -> int:
        return int(os.getenv("TOUCH_THRESHOLD", "14000"))

    @property
    def mqtt_client_id(self) -> str | None:
        return os.getenv("MQTT_CLIENT_ID")

    @property
    def mqtt_prefix(self) -> str:
        return os.getenv("MQTT_PREFIX", "sensors")

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

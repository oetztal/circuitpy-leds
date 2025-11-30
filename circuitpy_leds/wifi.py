from .config import Config
import wifi
from socketpool import SocketPool

def wifi_connect(config: Config) -> SocketPool:
    print("connect to WLAN")
    try:
        wifi.radio.connect(
            config.wifi_ssid, config.wifi_password
        )
        print(f"IP address: {wifi.radio.ipv4_address}")
    except Exception as e:
        print("wifi_connect() failed:", e)

    return SocketPool(wifi.radio)
import adafruit_logging
import adafruit_minimqtt.adafruit_minimqtt as MQTT
from socketpool import SocketPool

from . import Config


def connect(mqtt_client, userdata, flags, rc):
    print(f"Connected to MQTT Broker. flags {flags}, RC: {rc}")


def disconnect(mqtt_client, userdata, rc):
    print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    print("Published to {0} with PID {1}".format(topic, pid))


class MQTTClient:

    def __init__(self, pool: SocketPool, config: Config):
        print("Initializing MQTT Client", config.mqtt_host, config.mqtt_port, config.mqtt_client_id, pool)
        self.mqtt_client = MQTT.MQTT(
            broker=config.mqtt_host,
            port=config.mqtt_port,
            client_id=config.mqtt_client_id,
            socket_pool=pool,
            is_ssl=False,
            socket_timeout=0.1
        )

        # Connect callback handlers to mqtt_client
        self.mqtt_client.on_connect = connect
        self.mqtt_client.on_disconnect = disconnect
        self.mqtt_client.on_subscribe = subscribe
        self.mqtt_client.on_unsubscribe = unsubscribe
        self.mqtt_client.on_message = self.__on_message
        if False:
            self.mqtt_client.enable_logger(adafruit_logging, adafruit_logging.DEBUG)

        self.received_messages = []

    def __on_message(self, client, topic, message):
        print("New message on topic {0}: {1}".format(topic, message))
        self.received_messages.append(message)

    def publish(self, topic: str, message: str):
        try:
            self.mqtt_client.publish(topic, message, qos=1, retain=False)
        except OSError as e:
            print("Exception:", type(e), e)
            try:
                reconnect = self.mqtt_client.reconnect(False)
                print(f"Reconnecting to MQTT: {reconnect}")
            except:
                pass
        except MQTT.MMQTTException as e:
            print("Exception:", type(e), e)

    def connect(self):
        print("Connecting to MQTT Broker...")
        self.mqtt_client.connect()

    def subscribe(self, topic: str):
        print(f"Subscribing to {topic}")
        self.mqtt_client.subscribe(topic)

    def loop(self):
        self.mqtt_client.loop(0.1)

    def pop_message(self) -> str:
        return self.received_messages.pop(0) if self.received_messages else None

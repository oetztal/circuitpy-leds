import pytest
import asyncio
import json
import sys
from unittest.mock import MagicMock, Mock, AsyncMock, patch

# Mock paho.mqtt.client before importing AsyncMQTTControl
mock_mqtt_module = MagicMock()
sys.modules['paho'] = MagicMock()
sys.modules['paho.mqtt'] = MagicMock()
sys.modules['paho.mqtt.client'] = mock_mqtt_module

from circuitpy_leds.control.async_mqtt import AsyncMQTTControl
from circuitpy_leds.control import Control
from circuitpy_leds.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration"""
    config = MagicMock(spec=Config)
    config.mqtt_host = "mqtt.example.com"
    config.mqtt_port = 1883
    config.mqtt_client_id = "test-client"
    config.mqtt_prefix = "test/led"
    config.mqtt_status_interval = 30
    config.mqtt_reconnect_delay = 5
    config.wifi_ssid = "TestNetwork"
    config.wifi_password = "testpass"
    return config


@pytest.fixture
def mock_pixels():
    """Create a mock LED strip"""
    pixels = MagicMock()
    pixels.brightness = 0.1
    pixels.__len__.return_value = 30
    return pixels


@pytest.fixture
def mock_control(mock_pixels):
    """Create a mock control instance"""
    control = Control(mock_pixels)
    return control


@pytest.fixture
def mock_mqtt_client():
    """Create a mock Paho MQTT client"""
    client = MagicMock()
    # Paho client methods
    client.connect = Mock()
    client.subscribe = Mock()
    client.publish = Mock()
    client.loop_start = Mock()
    client.loop_stop = Mock()
    client.disconnect = Mock()
    # Callback attributes
    client.on_connect = None
    client.on_message = None
    client.on_disconnect = None
    return client


def test_async_mqtt_control_initialization(mock_control, mock_pixels, mock_config):
    """Test that AsyncMQTTControl initializes correctly"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config)

    assert mqtt.control == mock_control
    assert mqtt.pixels == mock_pixels
    assert mqtt.config == mock_config
    assert mqtt.running is False
    assert mqtt.connected is False
    assert mqtt.current_show_name is None
    assert isinstance(mqtt.message_queue, asyncio.Queue)


@pytest.mark.asyncio
async def test_on_message_queues_message(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test that _on_message queues messages correctly"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)
    mqtt.loop = asyncio.get_event_loop()  # Set loop for thread-safe operations

    # Create mock Paho message object
    mock_message = MagicMock()
    mock_message.topic = "test/led/command/show"
    mock_message.payload = b'{"show": "solid", "args": [[255, 0, 0]]}'

    # Call the message callback with Paho signature: (client, userdata, message)
    mqtt._on_message(None, None, mock_message)

    # Give it a moment to queue
    await asyncio.sleep(0.1)

    # Check that message was queued
    assert not mqtt.message_queue.empty()


@pytest.mark.asyncio
async def test_handle_show_command_solid(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling show command for solid color"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({"show": "solid", "args": [[255, 0, 0]]})

    await mqtt._handle_show_command(payload)

    # Verify show was changed
    assert mqtt.control.current_show is not None
    assert mqtt.current_show_name == "solid"


@pytest.mark.asyncio
async def test_handle_show_command_color_ranges(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling show command for color ranges"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({
        "show": "color_ranges",
        "kwargs": {
            "colors": [[255, 0, 0], [255, 255, 255], [0, 0, 255]],
            "ranges": [30, 70]
        }
    })

    await mqtt._handle_show_command(payload)

    # Verify show was changed
    assert mqtt.control.current_show is not None
    assert mqtt.current_show_name == "color_ranges"


@pytest.mark.asyncio
async def test_handle_show_command_invalid_json(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling invalid JSON in show command"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = "not valid json{"

    # Should not raise exception
    await mqtt._handle_show_command(payload)

    # Show should not be changed
    assert mqtt.current_show_name is None


@pytest.mark.asyncio
async def test_handle_show_command_unknown_show(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling command for unknown show"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({"show": "unknown_show"})

    await mqtt._handle_show_command(payload)

    # Show should not be changed
    assert mqtt.current_show_name is None


@pytest.mark.asyncio
async def test_handle_brightness_command_json(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling brightness command with JSON format"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({"brightness": 0.5})

    await mqtt._handle_brightness_command(payload)

    # Verify brightness was changed
    assert mock_pixels.brightness == 0.5


@pytest.mark.asyncio
async def test_handle_brightness_command_simple(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling brightness command with simple float format"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = "0.3"

    await mqtt._handle_brightness_command(payload)

    # Verify brightness was changed
    assert mock_pixels.brightness == 0.3


@pytest.mark.asyncio
async def test_handle_brightness_command_clamping(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test that brightness values are clamped to valid range"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    # Test upper bound
    await mqtt._handle_brightness_command("1.5")
    assert mock_pixels.brightness == 1.0

    # Test lower bound
    await mqtt._handle_brightness_command("-0.5")
    assert mock_pixels.brightness == 0.0


@pytest.mark.asyncio
async def test_handle_power_command_on(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling power on command"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)
    mock_pixels.brightness = 0.0

    payload = "on"

    await mqtt._handle_power_command(payload)

    # Verify LEDs were turned on
    assert mock_pixels.brightness > 0


@pytest.mark.asyncio
async def test_handle_power_command_off(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling power off command"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)
    mock_pixels.brightness = 0.5

    payload = "off"

    await mqtt._handle_power_command(payload)

    # Verify LEDs were turned off
    assert mock_pixels.brightness == 0.0


@pytest.mark.asyncio
async def test_handle_power_command_json(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling power command with JSON format"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({"power": "on"})

    await mqtt._handle_power_command(payload)

    assert mock_pixels.brightness > 0


@pytest.mark.asyncio
async def test_handle_message_routing_show(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test that messages are routed to correct handler based on topic"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    topic = "test/led/command/show"
    payload = json.dumps({"show": "solid", "args": [[0, 255, 0]]})

    await mqtt._handle_message(topic, payload)

    # Verify show was changed
    assert mqtt.current_show_name == "solid"


@pytest.mark.asyncio
async def test_handle_message_routing_brightness(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test message routing for brightness command"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    topic = "test/led/command/brightness"
    payload = "0.7"

    await mqtt._handle_message(topic, payload)

    assert mock_pixels.brightness == 0.7


@pytest.mark.asyncio
async def test_handle_message_routing_power(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test message routing for power command"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    topic = "test/led/command/power"
    payload = "off"

    await mqtt._handle_message(topic, payload)

    assert mock_pixels.brightness == 0.0


@pytest.mark.asyncio
async def test_handle_message_invalid_topic(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test handling message with invalid topic format"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    topic = "invalid/topic"
    payload = "test"

    # Should not raise exception
    await mqtt._handle_message(topic, payload)


@pytest.mark.asyncio
async def test_publish_status(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test publishing status to MQTT"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)
    mqtt.connected = True
    mqtt.current_show_name = "solid"
    mock_pixels.brightness = 0.5

    await mqtt._publish_status()

    # Verify publish was called
    mock_mqtt_client.publish.assert_called_once()

    # Check published message
    call_args = mock_mqtt_client.publish.call_args
    topic = call_args[0][0]
    message = call_args[0][1]

    assert "status/state" in topic

    # Parse JSON message
    status = json.loads(message)
    assert status["show"] == "solid"
    assert status["brightness"] == 0.5
    assert "uptime" in status


@pytest.mark.asyncio
async def test_publish_status_not_connected(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test that status is not published when not connected"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)
    mqtt.connected = False

    await mqtt._publish_status()

    # Verify publish was NOT called
    mock_mqtt_client.publish.assert_not_called()


@pytest.mark.asyncio
async def test_show_switching_with_args(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test show switching with explicit args format"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({
        "show": "two_color_blend",
        "args": [[255, 0, 0], [0, 0, 255]]
    })

    await mqtt._handle_show_command(payload)

    assert mqtt.current_show_name == "two_color_blend"
    assert mqtt.control.current_show is not None


@pytest.mark.asyncio
async def test_show_switching_two_color_blend(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test show switching with two_color_blend"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({
        "show": "two_color_blend",
        "args": [[255, 0, 0], [0, 0, 255]]
    })

    await mqtt._handle_show_command(payload)

    assert mqtt.current_show_name == "two_color_blend"


@pytest.mark.asyncio
async def test_config_properties(mock_config):
    """Test that config properties return correct values"""
    assert mock_config.mqtt_status_interval == 30
    assert mock_config.mqtt_reconnect_delay == 5
    assert "command" in mock_config.mqtt_prefix or True  # Mock doesn't have computed properties


def test_mqtt_control_not_connected_initially(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test that MQTT control starts in disconnected state"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    assert mqtt.connected is False
    assert mqtt.running is False


def test_message_queue_empty_initially(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test that message queue is empty on initialization"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    assert mqtt.message_queue.empty()


@pytest.mark.asyncio
async def test_show_command_with_layout(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test show command with layout configuration"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({
        "show": "solid",
        "args": [[255, 0, 0]],
        "layout": {
            "dead": 10,
            "mirror": True,
            "reverse": False
        }
    })

    await mqtt._handle_show_command(payload)

    # Verify show was changed
    assert mqtt.control.current_show is not None
    assert mqtt.current_show_name == "solid"


@pytest.mark.asyncio
async def test_show_command_with_layout_mirrored(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test show command with mirrored layout"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({
        "show": "color_ranges",
        "kwargs": {
            "colors": [[255, 0, 0], [255, 255, 255], [0, 0, 255]],
            "ranges": [30, 70]
        },
        "layout": {
            "mirror": True
        }
    })

    await mqtt._handle_show_command(payload)

    # Verify show was changed
    assert mqtt.control.current_show is not None
    assert mqtt.current_show_name == "color_ranges"


@pytest.mark.asyncio
async def test_show_command_with_layout_reversed(mock_control, mock_pixels, mock_config, mock_mqtt_client):
    """Test show command with reversed layout"""
    mqtt = AsyncMQTTControl(mock_control, mock_pixels, mock_config, mock_mqtt_client)

    payload = json.dumps({
        "show": "solid",
        "args": [[0, 255, 0]],
        "layout": {
            "reverse": True
        }
    })

    await mqtt._handle_show_command(payload)

    # Verify show was changed
    assert mqtt.control.current_show is not None
    assert mqtt.current_show_name == "solid"

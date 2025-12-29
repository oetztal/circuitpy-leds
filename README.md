[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=oetztal_circuitpy-leds&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=oetztal_circuitpy-leds)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=oetztal_circuitpy-leds&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=oetztal_circuitpy-leds)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=oetztal_circuitpy-leds&metric=coverage)](https://sonarcloud.io/summary/new_code?id=oetztal_circuitpy-leds)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=oetztal_circuitpy-leds&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=oetztal_circuitpy-leds)

# circuitpy-leds

A Python library for controlling LED strips using CircuitPython with async effects, MQTT/touch control, and flexible layout management.

## Features

- **10+ Built-in Effects**: Rainbow, color chase, starlight, bouncing balls, and more
- **Async Architecture**: Non-blocking effects using Python's asyncio
- **Flexible Layout System**: Support for mirrored, reversed, and dead LED configurations
- **Multiple Control Methods**: MQTT, touch sensors, or direct API control
- **Hardware Support**: NeoPixel and APA102 LED strips
- **Smooth Transitions**: Built-in color blending for seamless effect changes

## Effects

The following LED effects are currently implemented:

- **Solid** - Displays a single solid color across all LEDs with smooth blending transitions
- **Rainbow** - Rotates a rainbow color wheel around the strip with smooth color gradients
- **Color Run** - Random colored dots race across the strip at varying speeds
- **Starlight** - Simulates twinkling stars with random LED activations that fade in and out
- **Theater Chase** - Classic theater marquee chase pattern with rotating color wheel
- **Two Color Blend** - Smooth gradient blend between two colors across the strip
- **Color Ranges** - Display solid color sections with sharp transitions (perfect for flags)
- **Jump** - Animated bouncing balls with different heights and colors (physics-based simulation)
- **Wave** - Emits pulsing waves from the center with oscillating brightness and exponential decay towards the ends

All effects are implemented as async classes and can be controlled via touch input, MQTT, or TCP.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Basic Show Control](#basic-show-control)
  - [Using Layouts](#using-layouts)
  - [MQTT Control](#mqtt-control)
- [Available Shows](#available-shows)
- [Configuration](#configuration)
- [Hardware Setup](#hardware-setup)
- [Development](#development)

## Installation

### For CircuitPython Devices

Install CircuitPython dependency updater:

Install CircuitPython dependency updater

```
pip install circup
```

Install dependencies using

```
circup install -r requirements_cpy.txt
```

Install code using:

```bash
./install.py
```

### For Development

```bash
# Clone the repository
git clone https://github.com/oetztal/circuitpy-leds.git
cd circuitpy-leds

# Install with development dependencies
uv sync --dev

# Run tests
uv run pytest
```

## Quick Start

```python
import asyncio
from circuitpy_leds import Strip
from circuitpy_leds.shows import Rainbow, Solid

# Create a mock strip for testing (replace with actual hardware)
class MockStrip(Strip):
    def __init__(self, num_leds):
        self.num_leds = num_leds
        self.leds = [(0, 0, 0)] * num_leds

    def __len__(self):
        return self.num_leds

    def __setitem__(self, index, value):
        self.leds[index] = value

    def __getitem__(self, index):
        return self.leds[index]

    def fill(self, color):
        for i in range(self.num_leds):
            self.leds[i] = color

    def show(self):
        pass  # In real hardware, this updates the physical LEDs

# Create strip with 60 LEDs
strip = MockStrip(60)

# Create and run a rainbow effect
async def run_show():
    rainbow = Rainbow(strip)
    for step in range(1000):
        await rainbow.execute(step)

asyncio.run(run_show())
```

## Usage Examples

### Basic Show Control

```python
import asyncio
from circuitpy_leds.shows import Solid, Rainbow, TheaterChase

# Switch between different shows
async def show_controller(strip):
    # Show solid red for 5 seconds
    solid = Solid(strip, color=(255, 0, 0))
    for _ in range(100):
        await solid.execute(0)

    # Switch to rainbow effect
    rainbow = Rainbow(strip)
    for step in range(500):
        await rainbow.execute(step)

    # Theater chase effect
    chase = TheaterChase(strip)
    for step in range(500):
        await chase.execute(step)
```

### Using Layouts

The Layout class allows you to map a logical LED space to a physical strip with various transformations:

```python
from circuitpy_leds.support.layout import Layout

# Example 1: Mirrored layout
# Physical: 300 LEDs, Logical: 150 LEDs (mirrored in center)
physical_strip = MockStrip(300)
mirrored = Layout(physical_strip, dead=0, mirror=True, reverse=False)

# Setting LED 0 sets both physical LED 0 and 299
mirrored[0] = (255, 0, 0)

# Example 2: Dead LEDs at start
# Physical: 300 LEDs, skip first 80, use remaining 220
layout_with_dead = Layout(physical_strip, dead=80, mirror=False, reverse=False)

# Logical LED 0 maps to physical LED 80
layout_with_dead[0] = (0, 255, 0)

# Example 3: Reversed and mirrored
# Reverses the logical order and mirrors in the center
reversed_mirror = Layout(physical_strip, dead=0, mirror=True, reverse=True)
```

### MQTT Control

```python
from circuitpy_leds.control.mqtt import MQTTControl

# Configure MQTT connection
mqtt_control = MQTTControl(
    broker="mqtt.example.com",
    port=1883,
    topic="home/leds/command"
)

# Publish commands to control the LEDs
# Message format: {"show": "rainbow", "params": {...}}
```

### ColorRanges for Flags

Perfect for displaying flags or multi-color sections:

```python
from circuitpy_leds.shows import ColorRanges

# Create a pride flag
colors = [
    (255, 0, 0),      # Red
    (255, 165, 0),    # Orange
    (255, 255, 0),    # Yellow
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (128, 0, 128),    # Purple
]

pride_flag = ColorRanges(strip, colors=colors)

async def display_flag():
    for step in range(100):
        await pride_flag.execute(step)
```

### Morse Code Messages

```python
from circuitpy_leds.shows import MorseCode

# Display "HELLO" in morse code
morse = MorseCode(
    strip,
    message="HELLO",
    speed=0.5,  # Speed multiplier
    sleep_time=0.05  # Frame delay
)

async def send_message():
    for step in range(1000):
        await morse.execute(step)
```

## Available Shows

| Show | Description | Parameters |
|------|-------------|------------|
| **Solid** | Single solid color with smooth blending | `color: tuple` |
| **Rainbow** | Rotating rainbow color wheel | None |
| **ColorRun** | Random colored dots racing at varying speeds | None |
| **Starlight** | Twinkling stars effect | `probability: float`, `length: float`, `fade: float` |
| **TheaterChase** | Theater marquee chase pattern | `num_steps_per_cycle: int` |
| **TwoColorBlend** | Smooth gradient between two colors | `color1: tuple`, `color2: tuple` |
| **ColorRanges** | Solid color sections (perfect for flags) | `colors: list`, `ranges: list` |
| **Jump** | Physics-based bouncing balls | `pause_sec: float` |
| **Wave** | Pulsing waves from center | `wave_speed: float`, `decay_rate: float`, `brightness_frequency: float`, `wavelength: float` |
| **MorseCode** | Display messages in Morse code | `message: str`, `speed: float` |

## Configuration

Create a `settings.toml` file for your project:

```toml
[leds]
num_leds = 300
brightness = 0.5

[mqtt]
broker = "mqtt.example.com"
port = 1883
topic_prefix = "home/leds"
```

## Hardware Setup

### NeoPixel (WS2812) Strips

```python
import board
import neopixel

# For CircuitPython devices
pixels = neopixel.NeoPixel(board.D18, 300, auto_write=False)
```

### APA102 Strips

```python
from circuitpy_leds.driver.apa102 import APA102
from circuitpy_leds.config import Config

config = Config(num_leds=300)
strip = APA102(config)
```

### Wiring

- **NeoPixel**: Connect data pin to GPIO, 5V power, common ground
- **APA102**: Connect data and clock pins, 5V power, common ground
- Use appropriate power supply for your LED count (60mA per LED at full white)

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=circuitpy_leds --cov-report=html

# Run specific test file
uv run pytest tests/shows/test_rainbow.py -v
```

### Project Structure

```
circuitpy-leds/
├── circuitpy_leds/
│   ├── shows/           # LED effect implementations
│   ├── support/         # Utilities (blend, color, layout)
│   ├── control/         # Control interfaces (MQTT, touch)
│   ├── driver/          # Hardware drivers (APA102, etc.)
│   └── config.py        # Configuration management
├── tests/               # Test suite
└── examples/            # Usage examples
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

### Attribution

Portions of this code are derived from the [102shows project](https://github.com/Yottabits/102shows) (GPL-2.0).
Please see individual file headers for specific attribution details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/oetztal/circuitpy-leds/issues)
- **Discussions**: [GitHub Discussions](https://github.com/oetztal/circuitpy-leds/discussions)

## Acknowledgments

- Built with [CircuitPython](https://circuitpython.org/)
- Inspired by [102shows](https://github.com/Yottabits/102shows)
- Uses [Adafruit CircuitPython libraries](https://github.com/adafruit/Adafruit_CircuitPython_Bundle)
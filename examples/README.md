# CircuitPy-LEDs Examples

This directory contains practical examples demonstrating various features of the circuitpy-leds library.

## Examples Overview

### 01_basic_rainbow.py
The simplest example - displays a rotating rainbow effect on an LED strip.
- **Difficulty**: Beginner
- **Concepts**: Basic show usage, async execution

### 02_switching_shows.py
Demonstrates how to switch between multiple different LED effects.
- **Difficulty**: Beginner
- **Concepts**: Multiple shows, cycling effects, timing

### 03_layout_mirror.py
Shows how to use the Layout class to create mirrored LED configurations.
- **Difficulty**: Intermediate
- **Concepts**: Layout class, mirroring, logical vs physical LEDs

### 04_color_ranges_flag.py
Displays various flags using the ColorRanges show.
- **Difficulty**: Intermediate
- **Concepts**: ColorRanges, custom color sets, visualization

## Running the Examples

All examples use a `MockStrip` class that simulates LED hardware. To run on real hardware:

1. Replace `MockStrip` with your actual strip implementation (NeoPixel, APA102, etc.)
2. Update the pin configurations for your hardware
3. Adjust the number of LEDs to match your physical strip

### On a Computer (Simulation)

```bash
# Run any example directly
python examples/01_basic_rainbow.py

# Or with uv
uv run python examples/01_basic_rainbow.py
```

### On CircuitPython Hardware

1. Copy the desired example to your CircuitPython device as `code.py`
2. Modify the strip initialization for your hardware:

```python
# For NeoPixel
import board
import neopixel
strip = neopixel.NeoPixel(board.D18, 30, auto_write=False)

# For APA102
from circuitpy_leds.driver.apa102 import APA102
from circuitpy_leds.config import Config
config = Config(num_leds=30)
strip = APA102(config)
```

3. Reset your device to run the example

## Hardware Setup

### NeoPixel (WS2812) Wiring
- Data pin → GPIO (e.g., D18)
- 5V → External power supply 5V
- GND → Common ground

### APA102 Wiring
- Data pin → GPIO (e.g., MOSI)
- Clock pin → GPIO (e.g., SCK)
- 5V → External power supply 5V
- GND → Common ground

### Power Considerations
- Each LED draws approximately 60mA at full white brightness
- Use an external power supply for more than 10-15 LEDs
- Connect grounds between your microcontroller and power supply

## Tips

1. **Start Simple**: Begin with `01_basic_rainbow.py` to verify your setup
2. **Adjust Brightness**: Reduce brightness to save power and reduce heat
3. **Frame Rate**: Adjust `sleep_time` in shows to control animation speed
4. **Testing**: Use `MockStrip` for development before deploying to hardware

## Creating Your Own Examples

Feel free to create your own examples! The basic pattern is:

```python
import asyncio
from circuitpy_leds import Strip
from circuitpy_leds.shows import YourShow

# Create strip (mock or real hardware)
strip = ...

# Create show
show = YourShow(strip, **params)

# Run show
async def main():
    step = 0
    while True:
        await show.execute(step)
        step += 1

asyncio.run(main())
```

## Contributing Examples

Have a cool example? We'd love to see it! Please submit a pull request with:
- Clear comments explaining what the code does
- A description in this README
- Any special hardware requirements noted

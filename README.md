# circuitpy-leds

Control a LED strip using CircuitPython

## Effects

The following LED effects are currently implemented:

- **Solid** - Displays a single solid color across all LEDs with smooth blending transitions
- **Rainbow** - Rotates a rainbow color wheel around the strip with smooth color gradients
- **Color Run** - Random colored dots race across the strip at varying speeds
- **Starlight** - Simulates twinkling stars with random LED activations that fade in and out
- **Theater Chase** - Classic theater marquee chase pattern with rotating color wheel
- **Two Color Blend** - Smooth gradient blend between two colors across the strip
- **Jump** - Animated bouncing balls with different heights and colors (physics-based simulation)
- **Wave** - Emits pulsing waves from the center with oscillating brightness and exponential decay towards the ends

All effects are implemented as async classes and can be controlled via touch input, MQTT, or TCP.

## Setup

Install CircuitPython dependency updater

```
pip install circup
```

Install dependencies using

```
circup install -r requirements_cpy.txt
```

Install code using

```
./install.py
```
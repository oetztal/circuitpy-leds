# AGENTS.md

This document outlines the technical standards, conventions, and configurations used in the circuitpy-leds project to help AI agents and developers understand and maintain consistency.

## Project Overview

Control a LED strip using CircuitPython on embedded devices (specifically targeting Adafruit QtPy ESP32-S3).

## Python Standards

### Version
- **Python Version**: 3.14+ (specified in `.python-version` and `pyproject.toml`)
- **Target Platform**: CircuitPython 10.0.3 on Adafruit QtPy ESP32-S3 (no PSRAM)

### Package Management
- **Tool**: `uv` (modern Python package manager)
- **Lock File**: `uv.lock` (version 1, revision 3)
- **Dependency Groups**:
  - Production dependencies in `[project.dependencies]`
  - Development dependencies in `[dependency-groups.dev]`

### Key Dependencies

#### Production
- `adafruit-circuitpython-neopixel>=6.3.18` - LED strip control

#### CircuitPython Runtime (via circup)
- `adafruit_connection_manager==3.1.6`
- `adafruit_pixelbuf==2.0.10`
- `adafruit_ticks==1.1.5`
- `neopixel==6.3.18`
- `adafruit_logging==5.5.6`
- `adafruit_minimqtt==8.0.3`
- `asyncio==3.0.3`

#### Development
- `circup>=2.3.0` - CircuitPython library manager
- `mock>=5.2.0` - Testing mocks
- `pytest>=8.4.2` - Testing framework
- `pytest-cover>=3.0.0` - Code coverage
- `setuptools>=80.9.0` - Build tools

## Code Style & Conventions

### General Python Style
- **No explicit linter configuration** (no black, ruff, flake8, pylint configs present)
- **Import Style**: Standard library imports first, then third-party, then local (as seen in source files)
- **Blank Lines**: Two blank lines between top-level definitions
- **String Quotes**: No enforced preference (both single and double quotes used)

### Naming Conventions
- **Classes**: PascalCase (e.g., `Starlight`, `SmoothBlend`, `Config`)
- **Functions/Methods**: snake_case (e.g., `run_effect`, `wifi_connect`, `control_touch`)
- **Variables**: snake_case (e.g., `num_leds`, `delta_time`, `start_time`)
- **Constants**: UPPER_CASE (e.g., `WIFI_SSID`, `MQTT_HOST`)

### Async/Await Patterns
- Heavy use of `asyncio` for concurrent LED control and input handling
- Async functions defined with `async def`
- Tasks created with `asyncio.create_task()`
- Coordination with `asyncio.gather()`
- Small sleep intervals in loops: `await asyncio.sleep(0.05)`

### Type Hints
- Type hints used in function signatures (e.g., `config: Config`, `pixels: NeoPixel`)
- Return type hints not consistently applied
- Generic types used where appropriate

## Project Structure

```
circuitpy-leds/
├── circuitpy_leds/          # Main package
│   ├── control/             # Control interfaces (MQTT, TCP, touch)
│   ├── shows/               # LED effect implementations
│   ├── support/             # Utility modules (blend, color, layout)
│   ├── config.py            # Configuration management
│   ├── mqtt.py              # MQTT client
│   └── wifi.py              # WiFi connectivity
├── tests/                   # Test suite
│   ├── support/             # Tests for support modules
│   └── conftest.py          # Pytest configuration/fixtures
├── main.py                  # Entry point for CircuitPython device
├── install.py               # Installation script for device
├── settings.toml            # Configuration file (WiFi, MQTT settings)
├── requirements_cpy.txt     # CircuitPython dependencies
└── pyproject.toml           # Project metadata and dependencies
```

## Testing Standards

### Framework
- **Tool**: pytest
- **Coverage**: `pytest-cover` for code coverage reporting
- **Mocking**: `mock` library for unit testing

### Test Structure
- Tests organized in `tests/` directory mirroring source structure
- Fixtures defined in `conftest.py`
- Parameterized tests using `@pytest.mark.parametrize`

### Test Naming
- Test files: `test_*.py`
- Test functions: `test_*`
- Descriptive names indicating what is being tested

### Example Test Patterns
```python
@pytest.mark.parametrize(
    "delta_time,expected_value", [
        (0.0, 0),
        (1, 127.5),
        (2, 255),
    ]
)
def test_blend_one_led(mock_strip, mock_time_monotonic, delta_time, expected_value):
    # Test implementation
```

## CI/CD

### GitHub Actions Workflow
- **Trigger**: Push and pull requests to `main` branch
- **Runner**: Ubuntu latest
- **Steps**:
  1. Checkout code
  2. Set up Python (version from `.python-version`)
  3. Install `uv`
  4. Install dependencies: `uv sync --locked --all-extras --dev`
  5. Run tests: `uv run pytest tests --cov=circuitpy_leds --cov-report xml:reports/coverage.xml --cov-report term --junitxml=reports/junit.xml`

### Coverage Reports
- XML format: `reports/coverage.xml`
- Terminal output during CI
- JUnit XML: `reports/junit.xml`

## Configuration Files

### settings.toml
Contains device-specific configuration:
- WiFi credentials (`WIFI_SSID`, `WIFI_PASSWORD`)
- MQTT settings (`MQTT_HOST`, `MQTT_PREFIX`)
- Device mapping (`DEVICE_MAP`)
- Location data (`ELEVATION`)

**Note**: This file contains secrets and should be treated as sensitive.

### requirements_cpy.txt
CircuitPython-specific dependencies managed by `circup`. Includes device detection header.

## Hardware-Specific Considerations

### Target Device
- **Board**: Adafruit QtPy ESP32-S3 (no PSRAM variant)
- **CircuitPython Version**: 10.0.3
- **Mount Point**: `/Volumes/CIRCUITPY`

### LED Control
- **Library**: NeoPixel (WS2812/WS2811 addressable LEDs)
- **Color Format**: RGB tuples `(red, green, blue)` with values 0-255
- **Auto Write**: Disabled (`auto_write=False`), explicit `pixels.show()` required
- **Brightness**: Configurable (default 0.1 in main.py)

## Design Patterns

### Show/Effect Pattern
LED effects implemented as classes with:
- `__init__` method taking `Config` and effect-specific parameters
- `async execute(pixels: NeoPixel, index: int)` method
- Internal state management
- Non-blocking operation with `asyncio.sleep()`

### Control Pattern
Control interfaces follow async pattern:
- Separate modules for different control methods (MQTT, TCP, touch)
- Control task runs concurrently with effect rendering
- Modifies shared `Control` object to change active effect

## Installation & Deployment

### Development Setup
```bash
# Install dependencies
pip install circup
uv sync --locked --all-extras --dev
```

### Device Deployment
```bash
# Install CircuitPython libraries
circup install -r requirements_cpy.txt

# Deploy code to device
./install.py
```

## Git Standards

### Main Branch
- **Primary Branch**: `main`
- **Protection**: CI must pass for PRs

### Commit Style
Based on recent commits:
- Lowercase imperative mood (e.g., "improve settings defaults", "add test", "fix package name collision")
- Concise single-line messages
- No conventional commit prefixes enforced

## Notes for AI Agents

- This is a hardware-interfacing project with constraints from CircuitPython's limited stdlib
- Memory efficiency is important for embedded targets
- Async/await is central to the architecture for coordinating multiple tasks
- No traditional web framework or database involved
- Testing uses mocks extensively since hardware isn't available in CI
- Configuration is file-based (TOML) rather than environment variables

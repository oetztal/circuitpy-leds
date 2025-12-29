import pytest
from unittest.mock import MagicMock
import asyncio

from circuitpy_leds.shows.rainbow import Rainbow


def test_rainbow_initialization():
    """Test that Rainbow initializes correctly"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    rainbow = Rainbow(mock_strip)

    assert rainbow.strip is mock_strip
    assert rainbow.num_leds == 30
    assert rainbow.scale_factor == 255 / 30


@pytest.mark.asyncio
async def test_rainbow_execute_calls_strip():
    """Test that execute sets colors and calls show"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    rainbow = Rainbow(mock_strip)

    # Execute one step
    await rainbow.execute(current_step=0)

    # Should set all LED colors
    assert mock_strip.__setitem__.call_count == 10
    # Should call show() once
    mock_strip.show.assert_called_once()


@pytest.mark.asyncio
async def test_rainbow_colors_change_with_step():
    """Test that colors rotate as step increases"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10
    calls_step_0 = []
    calls_step_100 = []

    rainbow = Rainbow(mock_strip)

    # Capture colors at step 0
    def capture_step_0(index, color):
        calls_step_0.append((index, color))
    mock_strip.__setitem__.side_effect = capture_step_0
    await rainbow.execute(current_step=0)

    # Reset and capture colors at step 100
    mock_strip.__setitem__.call_count = 0
    mock_strip.__setitem__.side_effect = None
    calls_step_100 = []
    def capture_step_100(index, color):
        calls_step_100.append((index, color))
    mock_strip.__setitem__.side_effect = capture_step_100
    await rainbow.execute(current_step=100)

    # Colors should be different at different steps (rotation)
    assert calls_step_0[0][1] != calls_step_100[0][1], "Colors should rotate with step"


@pytest.mark.asyncio
async def test_rainbow_covers_all_leds():
    """Test that rainbow sets color for every LED"""
    mock_strip = MagicMock()
    num_leds = 30
    mock_strip.__len__.return_value = num_leds
    set_indices = set()

    def track_index(index, color):
        set_indices.add(index)

    mock_strip.__setitem__.side_effect = track_index

    rainbow = Rainbow(mock_strip)
    await rainbow.execute(current_step=0)

    # Should have set all LEDs from 0 to num_leds-1
    assert set_indices == set(range(num_leds))


@pytest.mark.asyncio
async def test_rainbow_creates_gradient():
    """Test that neighboring LEDs have different colors (gradient effect)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10
    colors = {}

    def capture_color(index, color):
        colors[index] = color

    mock_strip.__setitem__.side_effect = capture_color

    rainbow = Rainbow(mock_strip)
    await rainbow.execute(current_step=0)

    # Check that adjacent LEDs have different colors (gradient)
    for i in range(len(colors) - 1):
        assert colors[i] != colors[i + 1], f"LED {i} and {i+1} should have different colors"

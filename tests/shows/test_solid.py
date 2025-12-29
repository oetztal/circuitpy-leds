import pytest
from unittest.mock import MagicMock, patch
import asyncio

from circuitpy_leds.shows.solid import Solid


def test_solid_initialization():
    """Test that Solid initializes correctly"""
    mock_strip = MagicMock()
    test_color = (255, 128, 0)

    solid = Solid(mock_strip, test_color)

    assert solid.strip is mock_strip
    assert solid.color == test_color
    assert solid.blend is None


@pytest.mark.asyncio
async def test_solid_creates_blend_on_first_execute():
    """Test that blend is created on first execute call"""
    mock_strip = MagicMock()
    test_color = (255, 0, 0)

    with patch('circuitpy_leds.shows.solid.SmoothBlend') as mock_blend_class:
        mock_blend_instance = MagicMock()
        mock_blend_class.return_value = mock_blend_instance

        solid = Solid(mock_strip, test_color)
        assert solid.blend is None

        # First execute should create blend
        await solid.execute(0)

        # Blend should be created with correct parameters
        mock_blend_class.assert_called_once_with(mock_strip, test_color)
        assert solid.blend is not None


@pytest.mark.asyncio
async def test_solid_reuses_blend_on_subsequent_calls():
    """Test that blend is reused on subsequent execute calls"""
    mock_strip = MagicMock()
    test_color = (0, 255, 0)

    with patch('circuitpy_leds.shows.solid.SmoothBlend') as mock_blend_class:
        mock_blend_instance = MagicMock()
        mock_blend_class.return_value = mock_blend_instance

        solid = Solid(mock_strip, test_color)

        # Execute multiple times
        await solid.execute(0)
        await solid.execute(1)
        await solid.execute(2)

        # Blend should only be created once
        mock_blend_class.assert_called_once()
        # But step should be called three times
        assert mock_blend_instance.step.call_count == 3


@pytest.mark.asyncio
async def test_solid_calls_blend_step():
    """Test that execute calls blend.step()"""
    mock_strip = MagicMock()
    test_color = (0, 0, 255)

    with patch('circuitpy_leds.shows.solid.SmoothBlend') as mock_blend_class:
        mock_blend_instance = MagicMock()
        mock_blend_class.return_value = mock_blend_instance

        solid = Solid(mock_strip, test_color)

        await solid.execute(0)

        # step should be called once
        mock_blend_instance.step.assert_called_once()


@pytest.mark.asyncio
async def test_solid_with_different_colors():
    """Test solid with various color values"""
    mock_strip = MagicMock()

    test_colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (128, 128, 128),  # Gray
        (0, 0, 0),      # Black
    ]

    for color in test_colors:
        with patch('circuitpy_leds.shows.solid.SmoothBlend') as mock_blend_class:
            solid = Solid(mock_strip, color)
            await solid.execute(0)

            # Verify blend was created with correct color
            mock_blend_class.assert_called_once_with(mock_strip, color)

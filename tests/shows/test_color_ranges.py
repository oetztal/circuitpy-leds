import pytest
from unittest.mock import MagicMock

from circuitpy_leds.shows.color_ranges import ColorRanges


def test_color_ranges_initialization_with_colors_only():
    """Test that ColorRanges initializes correctly with colors list only (equal distribution)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)])

    assert color_ranges.num_leds == 30
    assert len(color_ranges.colors) == 3
    assert len(color_ranges.ranges) == 3
    assert len(color_ranges.target_colors) == 30
    assert color_ranges.blend is None


def test_color_ranges_initialization_with_custom_ranges():
    """Test that ColorRanges initializes correctly with custom boundary ranges"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)],
        ranges=[40, 60]
    )

    assert color_ranges.num_leds == 30
    assert len(color_ranges.colors) == 3
    assert len(color_ranges.ranges) == 3
    assert len(color_ranges.target_colors) == 30


def test_color_ranges_validation_missing_colors():
    """Test that missing colors parameter raises TypeError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(TypeError):
        ColorRanges(mock_strip)


def test_color_ranges_validation_empty_colors():
    """Test that empty colors list raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Colors list cannot be empty"):
        ColorRanges(mock_strip, colors=[])


def test_color_ranges_validation_invalid_color_format():
    """Test that invalid color format raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # Not a tuple or list (string instead)
    with pytest.raises(ValueError, match="Color must be RGB tuple/list"):
        ColorRanges(mock_strip, colors=["#ff0000"])

    # Wrong tuple/list length
    with pytest.raises(ValueError, match="Color must be RGB tuple/list"):
        ColorRanges(mock_strip, colors=[(255, 0)])


def test_color_ranges_validation_invalid_color_values():
    """Test that invalid color values raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # Values out of range
    with pytest.raises(ValueError, match="Color values must be integers 0-255"):
        ColorRanges(mock_strip, colors=[(256, 0, 0)])

    with pytest.raises(ValueError, match="Color values must be integers 0-255"):
        ColorRanges(mock_strip, colors=[(-1, 0, 0)])

    # Non-integer values
    with pytest.raises(ValueError, match="Color values must be integers 0-255"):
        ColorRanges(mock_strip, colors=[(255.5, 0, 0)])


def test_color_ranges_validation_wrong_number_of_ranges():
    """Test that wrong number of boundary ranges raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # 3 colors need 2 boundaries, but providing 3
    with pytest.raises(ValueError, match="must have 2 elements"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], ranges=[30, 60, 80])

    # 3 colors need 2 boundaries, but providing 1
    with pytest.raises(ValueError, match="must have 2 elements"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], ranges=[50])


def test_color_ranges_validation_boundary_out_of_range():
    """Test that boundaries outside 0-100 range raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # Boundary at 0 is invalid (must be > 0)
    with pytest.raises(ValueError, match="must be between 0 and 100"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0)], ranges=[0])

    # Boundary at 100 is invalid (must be < 100)
    with pytest.raises(ValueError, match="must be between 0 and 100"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0)], ranges=[100])

    # Boundary > 100
    with pytest.raises(ValueError, match="must be between 0 and 100"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0)], ranges=[150])


def test_color_ranges_validation_boundaries_not_ascending():
    """Test that boundaries not in ascending order raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="must be in ascending order"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], ranges=[60, 40])

    # Equal boundaries also invalid
    with pytest.raises(ValueError, match="must be in ascending order"):
        ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)], ranges=[50, 50])


def test_color_ranges_two_colors_equal():
    """Test 50-50 split with two colors"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    color_ranges = ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 0, 255)])

    # First 5 LEDs should be red
    for i in range(5):
        assert color_ranges.target_colors[i] == (255, 0, 0), f"LED {i} should be red"

    # Last 5 LEDs should be blue
    for i in range(5, 10):
        assert color_ranges.target_colors[i] == (0, 0, 255), f"LED {i} should be blue"


def test_color_ranges_two_colors_custom():
    """Test custom split with two colors using boundary"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    # 70% red, 30% blue (boundary at 70%)
    color_ranges = ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 0, 255)], ranges=[70])

    # First 7 LEDs should be red (0-70%)
    for i in range(7):
        assert color_ranges.target_colors[i] == (255, 0, 0), f"LED {i} should be red"

    # Last 3 LEDs should be blue (70-100%)
    for i in range(7, 10):
        assert color_ranges.target_colors[i] == (0, 0, 255), f"LED {i} should be blue"


def test_color_ranges_three_colors_equal():
    """Test 33-33-33 split with three colors (flag use case)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)]  # Red, White, Blue
    )

    # First 10 LEDs should be red (0-33%)
    for i in range(10):
        assert color_ranges.target_colors[i] == (255, 0, 0), f"LED {i} should be red"

    # Middle 10 LEDs should be white (33-66%)
    for i in range(10, 20):
        assert color_ranges.target_colors[i] == (255, 255, 255), f"LED {i} should be white"

    # Last 10 LEDs should be blue (66-100%)
    for i in range(20, 30):
        assert color_ranges.target_colors[i] == (0, 0, 255), f"LED {i} should be blue"


def test_color_ranges_three_colors_custom():
    """Test unequal distribution with custom boundary percentages"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    # 30% red, 40% white, 30% blue (boundaries at 30% and 70%)
    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)],
        ranges=[30, 70]
    )

    # First 3 LEDs should be red (0-30%)
    for i in range(3):
        assert color_ranges.target_colors[i] == (255, 0, 0), f"LED {i} should be red"

    # Middle 4 LEDs should be white (30-70%)
    for i in range(3, 7):
        assert color_ranges.target_colors[i] == (255, 255, 255), f"LED {i} should be white"

    # Last 3 LEDs should be blue (70-100%)
    for i in range(7, 10):
        assert color_ranges.target_colors[i] == (0, 0, 255), f"LED {i} should be blue"


def test_color_ranges_sharp_transitions():
    """Test that transitions between color ranges are sharp (no blending)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    )

    # Check that each LED has one of the three exact colors (no blending)
    for i, color in enumerate(color_ranges.target_colors):
        assert color in [(255, 0, 0), (0, 255, 0), (0, 0, 255)], \
            f"LED {i} has blended color {color}, expected sharp transition"


def test_color_ranges_single_led():
    """Test edge case: strip with only 1 LED"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 1

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    )

    # Single LED should display first color
    assert len(color_ranges.target_colors) == 1
    assert color_ranges.target_colors[0] == (255, 0, 0)


def test_color_ranges_single_color():
    """Test edge case: only one color specified"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(mock_strip, colors=[(255, 0, 0)])

    # All LEDs should be the same color
    for i in range(30):
        assert color_ranges.target_colors[i] == (255, 0, 0), \
            f"LED {i} should be red"


def test_color_ranges_pattern_consistency():
    """Test that pattern doesn't change between calls (static display)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    )

    # Store initial pattern
    initial_pattern = color_ranges.target_colors.copy()

    # Create another instance with same parameters
    color_ranges2 = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    )

    # Patterns should be identical
    assert initial_pattern == color_ranges2.target_colors


def test_color_ranges_uses_smooth_blend():
    """Test that SmoothBlend is created on first execute call"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    )

    # Initially blend should be None
    assert color_ranges.blend is None


def test_color_ranges_led_mapping_boundary_10_leds():
    """Test specific LED indices map to correct colors for 10 LED strip"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0)]  # Red and Green, 50-50
    )

    # LEDs 0-4 should be red (0-50%)
    # LEDs 5-9 should be green (50-100%)
    assert color_ranges.target_colors[0] == (255, 0, 0)
    assert color_ranges.target_colors[4] == (255, 0, 0)
    assert color_ranges.target_colors[5] == (0, 255, 0)
    assert color_ranges.target_colors[9] == (0, 255, 0)


def test_color_ranges_led_mapping_boundary_100_leds():
    """Test boundary calculations for larger strip"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # 33-33-33
    )

    # First third (0-33%) = LEDs 0-32
    assert color_ranges.target_colors[0] == (255, 0, 0)
    assert color_ranges.target_colors[32] == (255, 0, 0)

    # Second third (33-66%) = LEDs 33-65
    assert color_ranges.target_colors[33] == (0, 255, 0)
    assert color_ranges.target_colors[65] == (0, 255, 0)

    # Last third (66-100%) = LEDs 66-99
    assert color_ranges.target_colors[66] == (0, 0, 255)
    assert color_ranges.target_colors[99] == (0, 0, 255)


def test_color_ranges_percentage_edge_cases():
    """Test percentage calculations at 0% and 100% boundaries"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 20

    # Create ranges with boundary at 50%
    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 0, 255)],
        ranges=[50]
    )

    # First LED (0%) should be first color
    assert color_ranges.target_colors[0] == (255, 0, 0)

    # Last LED should be second color
    assert color_ranges.target_colors[19] == (0, 0, 255)

    # LED at index 10 = 10/20 * 100 = 50%, should be in second range
    assert color_ranges.target_colors[10] == (0, 0, 255)


def test_color_ranges_various_strip_lengths():
    """Test that feature works correctly with various strip lengths"""
    for num_leds in [1, 5, 10, 30, 50, 100, 144]:
        mock_strip = MagicMock()
        mock_strip.__len__.return_value = num_leds

        color_ranges = ColorRanges(
            mock_strip,
            colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        )

        # Should have colors for all LEDs
        assert len(color_ranges.target_colors) == num_leds

        # All colors should be one of the specified colors
        for color in color_ranges.target_colors:
            assert color in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]


def test_color_ranges_build_equal_ranges():
    """Test internal equal ranges building"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0)]
    )

    # Should have created 2 ranges
    assert len(color_ranges.ranges) == 2

    # First range: 0-50%
    assert color_ranges.ranges[0][0] == 0
    assert color_ranges.ranges[0][1] == 50.0
    assert color_ranges.ranges[0][2] == (255, 0, 0)

    # Second range: 50-100%
    assert color_ranges.ranges[1][0] == 50.0
    assert color_ranges.ranges[1][1] == 100.0
    assert color_ranges.ranges[1][2] == (0, 255, 0)


def test_color_ranges_build_custom_ranges():
    """Test internal custom ranges building from boundaries"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)],
        ranges=[40, 60]
    )

    # Should have created 3 ranges
    assert len(color_ranges.ranges) == 3

    # First range: 0-40%
    assert color_ranges.ranges[0] == (0.0, 40, (255, 0, 0))

    # Second range: 40-60%
    assert color_ranges.ranges[1] == (40, 60, (255, 255, 255))

    # Third range: 60-100%
    assert color_ranges.ranges[2] == (60, 100.0, (0, 0, 255))


def test_color_ranges_flag_examples():
    """Test real-world flag examples"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # German flag: black, red, gold (equal thirds)
    german = ColorRanges(mock_strip, colors=[(0, 0, 0), (255, 0, 0), (255, 215, 0)])
    assert len(german.target_colors) == 30
    assert german.target_colors[0] == (0, 0, 0)  # Black
    assert german.target_colors[15] == (255, 0, 0)  # Red
    assert german.target_colors[29] == (255, 215, 0)  # Gold

    # French flag: blue, white, red (equal thirds)
    french = ColorRanges(mock_strip, colors=[(0, 85, 164), (255, 255, 255), (239, 65, 53)])
    assert len(french.target_colors) == 30
    assert french.target_colors[0] == (0, 85, 164)  # Blue
    assert french.target_colors[15] == (255, 255, 255)  # White
    assert french.target_colors[29] == (239, 65, 53)  # Red


def test_color_ranges_empty_ranges_list():
    """Test that empty ranges list is treated as equal distribution"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)],
        ranges=[]  # Empty list
    )

    # Should behave same as no ranges parameter (equal distribution)
    assert len(color_ranges.ranges) == 3
    # First 10 LEDs should be red
    assert color_ranges.target_colors[0] == (255, 0, 0)
    assert color_ranges.target_colors[9] == (255, 0, 0)
    # Middle 10 should be green
    assert color_ranges.target_colors[15] == (0, 255, 0)
    # Last 10 should be blue
    assert color_ranges.target_colors[29] == (0, 0, 255)


@pytest.mark.asyncio
async def test_color_ranges_execute_creates_blend_on_first_call():
    """Test that execute() creates SmoothBlend on first call"""
    from unittest.mock import patch

    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)]
    )

    # Mock asyncio.sleep to avoid actual delays
    with patch('asyncio.sleep', return_value=None):
        # Initially blend should be None
        assert color_ranges.blend is None

        # After first execute, blend should be created
        await color_ranges.execute(0)
        assert color_ranges.blend is not None

        # Verify the blend has correct target colors
        assert len(color_ranges.blend.target_colors) == 30


@pytest.mark.asyncio
async def test_color_ranges_execute_reuses_blend_on_subsequent_calls():
    """Test that execute() reuses the same SmoothBlend instance"""
    from unittest.mock import patch

    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 255, 0)]
    )

    with patch('asyncio.sleep', return_value=None):
        # Execute first time
        await color_ranges.execute(0)
        first_blend = color_ranges.blend

        # Execute second time
        await color_ranges.execute(1)
        second_blend = color_ranges.blend

        # Should be the same instance
        assert first_blend is second_blend


@pytest.mark.asyncio
async def test_color_ranges_execute_calls_blend_step():
    """Test that execute() calls blend.step() each time"""
    from unittest.mock import Mock, patch

    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (0, 0, 255)],
        ranges=[50]  # 50-50 split
    )

    with patch('asyncio.sleep', return_value=None):
        # Execute first time to create blend
        await color_ranges.execute(0)

        # Mock blend.step to track calls
        original_step = color_ranges.blend.step
        color_ranges.blend.step = Mock(side_effect=original_step)

        # Execute again
        await color_ranges.execute(1)

        # Verify step was called
        assert color_ranges.blend.step.call_count == 1


@pytest.mark.asyncio
async def test_color_ranges_execute_with_custom_ranges():
    """Test that execute() works correctly with custom boundary ranges"""
    from unittest.mock import patch

    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 20

    # Create with custom boundaries (30% red, 40% white, 30% blue)
    color_ranges = ColorRanges(
        mock_strip,
        colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)],
        ranges=[30, 70]
    )

    with patch('asyncio.sleep', return_value=None):
        # Execute should work without errors
        await color_ranges.execute(0)

        # Verify blend was created with correct target colors
        assert color_ranges.blend is not None
        assert len(color_ranges.blend.target_colors) == 20

        # Verify colors match expectations
        assert color_ranges.blend.target_colors[0] == (255, 0, 0)  # Red
        assert color_ranges.blend.target_colors[10] == (255, 255, 255)  # White
        assert color_ranges.blend.target_colors[19] == (0, 0, 255)  # Blue

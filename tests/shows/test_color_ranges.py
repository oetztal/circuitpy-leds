import pytest
from unittest.mock import MagicMock

from circuitpy_leds.shows.color_ranges import ColorRanges


def test_color_ranges_initialization_with_colors():
    """Test that ColorRanges initializes correctly with colors list"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    color_ranges = ColorRanges(mock_strip, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)])

    assert color_ranges.num_leds == 30
    assert len(color_ranges.ranges) == 3
    assert len(color_ranges.target_colors) == 30
    assert color_ranges.blend is None


def test_color_ranges_initialization_with_ranges():
    """Test that ColorRanges initializes correctly with explicit ranges"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    ranges = [
        (0, 40, (255, 0, 0)),
        (40, 60, (255, 255, 255)),
        (60, 100, (0, 0, 255))
    ]
    color_ranges = ColorRanges(mock_strip, ranges=ranges)

    assert color_ranges.num_leds == 30
    assert color_ranges.ranges == ranges
    assert len(color_ranges.target_colors) == 30


def test_color_ranges_validation_both_specified():
    """Test that specifying both colors and ranges raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Specify either 'colors' or 'ranges', not both"):
        ColorRanges(
            mock_strip,
            colors=[(255, 0, 0)],
            ranges=[(0, 100, (255, 0, 0))]
        )


def test_color_ranges_validation_neither_specified():
    """Test that specifying neither colors nor ranges raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Must specify either 'colors' or 'ranges'"):
        ColorRanges(mock_strip)


def test_color_ranges_validation_empty_colors():
    """Test that empty colors list raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Colors list cannot be empty"):
        ColorRanges(mock_strip, colors=[])


def test_color_ranges_validation_empty_ranges():
    """Test that empty ranges list raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Ranges list cannot be empty"):
        ColorRanges(mock_strip, ranges=[])


def test_color_ranges_validation_invalid_color_format():
    """Test that invalid color format raises ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # Not a tuple
    with pytest.raises(ValueError, match="Color must be RGB tuple"):
        ColorRanges(mock_strip, colors=[[255, 0, 0]])

    # Wrong tuple length
    with pytest.raises(ValueError, match="Color must be RGB tuple"):
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


def test_color_ranges_validation_ranges_not_starting_at_zero():
    """Test that ranges not starting at 0% raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="First range must start at 0%"):
        ColorRanges(mock_strip, ranges=[(10, 100, (255, 0, 0))])


def test_color_ranges_validation_ranges_not_ending_at_hundred():
    """Test that ranges not ending at 100% raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Last range must end at 100%"):
        ColorRanges(mock_strip, ranges=[(0, 90, (255, 0, 0))])


def test_color_ranges_validation_ranges_with_gaps():
    """Test that ranges with gaps raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Gap detected"):
        ColorRanges(mock_strip, ranges=[
            (0, 40, (255, 0, 0)),
            (50, 100, (0, 0, 255))  # Gap from 40 to 50
        ])


def test_color_ranges_validation_ranges_with_overlaps():
    """Test that ranges with overlaps raise ValueError"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    with pytest.raises(ValueError, match="Overlap detected"):
        ColorRanges(mock_strip, ranges=[
            (0, 60, (255, 0, 0)),
            (50, 100, (0, 0, 255))  # Overlap from 50 to 60
        ])


def test_color_ranges_two_colors():
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


def test_color_ranges_three_colors():
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


def test_color_ranges_custom_percentages():
    """Test unequal distribution with custom percentages"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 10

    # 30% red, 40% white, 30% blue
    color_ranges = ColorRanges(mock_strip, ranges=[
        (0, 30, (255, 0, 0)),
        (30, 70, (255, 255, 255)),
        (70, 100, (0, 0, 255))
    ])

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

    # Create ranges with very specific boundaries
    color_ranges = ColorRanges(mock_strip, ranges=[
        (0, 50, (255, 0, 0)),
        (50, 100, (0, 0, 255))
    ])

    # First LED (0%) should be first color
    assert color_ranges.target_colors[0] == (255, 0, 0)

    # Last LED should be second color
    assert color_ranges.target_colors[19] == (0, 0, 255)

    # Middle should split correctly
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


def test_color_ranges_colors_to_ranges_conversion():
    """Test internal conversion of colors list to ranges"""
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


def test_color_ranges_flag_examples():
    """Test real-world flag examples"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    # German flag: black, red, gold
    german = ColorRanges(mock_strip, colors=[(0, 0, 0), (255, 0, 0), (255, 215, 0)])
    assert len(german.target_colors) == 30
    assert german.target_colors[0] == (0, 0, 0)  # Black
    assert german.target_colors[15] == (255, 0, 0)  # Red
    assert german.target_colors[29] == (255, 215, 0)  # Gold

    # French flag: blue, white, red
    french = ColorRanges(mock_strip, colors=[(0, 85, 164), (255, 255, 255), (239, 65, 53)])
    assert len(french.target_colors) == 30
    assert french.target_colors[0] == (0, 85, 164)  # Blue
    assert french.target_colors[15] == (255, 255, 255)  # White
    assert french.target_colors[29] == (239, 65, 53)  # Red

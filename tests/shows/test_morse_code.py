import pytest
from unittest.mock import MagicMock

from circuitpy_leds.shows.morse_code import MorseCode, MORSE_CODE


def test_morse_code_dictionary_has_alphabet():
    """Verify morse code dictionary contains basic characters"""
    assert 'A' in MORSE_CODE
    assert 'Z' in MORSE_CODE
    assert '0' in MORSE_CODE
    assert '9' in MORSE_CODE
    assert MORSE_CODE['S'] == '...'
    assert MORSE_CODE['O'] == '---'


def test_morse_code_initialization():
    """Test that MorseCode initializes correctly"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    morse = MorseCode(mock_strip, message="HELLO", speed=0.5, sleep_time=0.05)

    assert morse.message == "HELLO"
    assert morse.speed == 0.5
    assert morse.sleep_time == 0.05
    assert morse.num_leds == 30
    assert len(morse.pattern) > 0
    assert morse.pattern_length > 0


def test_morse_code_pattern_building_simple():
    """Test pattern building for a simple message"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    morse = MorseCode(mock_strip, message="E")  # E = single dot

    # Pattern should contain at least the dot (1 LED) + padding
    assert len(morse.pattern) > 0
    # Should have some non-black LEDs (the actual morse code)
    assert any(color != (0, 0, 0) for color in morse.pattern)


def test_morse_code_pattern_has_spacing():
    """Test that pattern includes proper spacing"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    morse = MorseCode(mock_strip, message="SOS")  # Famous morse code

    # SOS = ... --- ...
    # Should have colored LEDs and black (spacing) LEDs
    has_colored = any(color != (0, 0, 0) for color in morse.pattern)
    has_black = any(color == (0, 0, 0) for color in morse.pattern)

    assert has_colored, "Pattern should have colored LEDs for morse code"
    assert has_black, "Pattern should have black LEDs for spacing"


def test_morse_code_multi_word_different_colors():
    """Test that different words get different colors"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 200

    morse = MorseCode(mock_strip, message="HI BYE")

    # Get all non-black colors from pattern
    colors = [color for color in morse.pattern if color != (0, 0, 0)]

    # Should have more than one unique color (one per word)
    unique_colors = set(colors)
    assert len(unique_colors) >= 2, "Multi-word message should have multiple colors"


def test_morse_code_handles_lowercase():
    """Test that lowercase input is converted to uppercase"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    morse = MorseCode(mock_strip, message="hello")

    assert morse.message == "HELLO"


def test_morse_code_handles_empty_message():
    """Test that empty message uses default"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    morse = MorseCode(mock_strip, message="")

    # Should use default message
    assert morse.message == "HELLO"
    assert len(morse.pattern) > 0


def test_morse_code_handles_unknown_characters():
    """Test that unknown characters are handled gracefully"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # Using a character not in MORSE_CODE (if any)
    morse = MorseCode(mock_strip, message="A~B")  # ~ might not be in morse

    # Should not crash and should produce a pattern
    assert len(morse.pattern) > 0


@pytest.mark.asyncio
async def test_morse_code_execute():
    """Test that execute method works without errors"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    morse = MorseCode(mock_strip, message="HI", speed=0.5, sleep_time=0.001)

    # Execute a few frames
    await morse.execute(0)
    await morse.execute(1)
    await morse.execute(10)

    # Verify strip methods were called
    assert mock_strip.show.called
    assert mock_strip.__setitem__.called


def test_morse_code_pattern_length_reasonable():
    """Test that pattern length is reasonable for the message"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # "E" is the shortest morse (single dot)
    morse_short = MorseCode(mock_strip, message="E")

    # "HELLO WORLD" is longer
    morse_long = MorseCode(mock_strip, message="HELLO WORLD")

    # Longer message should have longer pattern
    assert len(morse_long.pattern) > len(morse_short.pattern)

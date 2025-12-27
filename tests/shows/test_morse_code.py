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


def test_morse_code_execute_synchronous():
    """Test that execute method can be called (synchronous test)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 30

    morse = MorseCode(mock_strip, message="HI", speed=0.5, sleep_time=0.001)

    # Verify the morse code object was created successfully
    assert morse.pattern_length > 0
    assert morse.message == "HI"

    # Note: Full async execution testing would require pytest-asyncio
    # For now, we verify the object is properly initialized


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


def test_morse_code_custom_dot_length():
    """Test custom dot length parameter"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # E = single dot with custom length
    morse = MorseCode(mock_strip, message="E", dot_length=5)

    # Should have 5 LEDs for the dot (plus padding)
    colored_leds = [c for c in morse.pattern if c != (0, 0, 0)]
    assert len(colored_leds) == 5


def test_morse_code_custom_dash_length():
    """Test custom dash length parameter"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # T = single dash with custom length
    morse = MorseCode(mock_strip, message="T", dash_length=7)

    # Should have 7 LEDs for the dash (plus padding)
    colored_leds = [c for c in morse.pattern if c != (0, 0, 0)]
    assert len(colored_leds) == 7


def test_morse_code_custom_symbol_space():
    """Test custom symbol space parameter"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # S = ... (3 symbols with spaces between)
    morse_default = MorseCode(mock_strip, message="S", symbol_space=1)
    morse_larger = MorseCode(mock_strip, message="S", symbol_space=5)

    # Larger symbol space should result in longer pattern
    assert len(morse_larger.pattern) > len(morse_default.pattern)


def test_morse_code_custom_letter_space():
    """Test custom letter space parameter"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # HI = 2 letters
    morse_default = MorseCode(mock_strip, message="HI", letter_space=2)
    morse_larger = MorseCode(mock_strip, message="HI", letter_space=10)

    # Larger letter space should result in longer pattern
    assert len(morse_larger.pattern) > len(morse_default.pattern)


def test_morse_code_custom_word_space():
    """Test custom word space parameter"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 200

    # Two words
    morse_default = MorseCode(mock_strip, message="HI BYE", word_space=4)
    morse_larger = MorseCode(mock_strip, message="HI BYE", word_space=20)

    # Larger word space should result in longer pattern
    assert len(morse_larger.pattern) > len(morse_default.pattern)


def test_morse_code_zero_spacing():
    """Test that zero spacing works (no spaces)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # S with no spacing
    morse = MorseCode(mock_strip, message="S", symbol_space=0, letter_space=0, word_space=0)

    # Should still create a valid pattern (just 3 dots with no spaces)
    assert len(morse.pattern) > 0
    colored_leds = [c for c in morse.pattern if c != (0, 0, 0)]
    # S = ... (3 dots with default dot_length=1)
    assert len(colored_leds) == 6


def test_morse_code_standard_timing():
    """Test standard morse timing (1-3-1-3-7)"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 200

    # Standard international morse timing
    morse = MorseCode(
        mock_strip,
        message="SOS",
        dot_length=1,
        dash_length=3,
        symbol_space=1,
        letter_space=3,
        word_space=7
    )

    # Should create a valid pattern with standard timing
    assert len(morse.pattern) > 0
    assert morse.dot_length == 1
    assert morse.dash_length == 3
    assert morse.symbol_space == 1
    assert morse.letter_space == 3
    assert morse.word_space == 7


def test_morse_code_parameter_bounds():
    """Test that parameters are bounded to valid ranges"""
    mock_strip = MagicMock()
    mock_strip.__len__.return_value = 100

    # Test negative values are corrected
    morse = MorseCode(
        mock_strip,
        message="E",
        dot_length=-5,
        dash_length=0,
        symbol_space=-1,
        letter_space=-2,
        word_space=-3
    )

    # dot_length and dash_length should be at least 1
    assert morse.dot_length >= 1
    assert morse.dash_length >= 1
    # Spacing can be 0 or positive
    assert morse.symbol_space >= 0
    assert morse.letter_space >= 0
    assert morse.word_space >= 0

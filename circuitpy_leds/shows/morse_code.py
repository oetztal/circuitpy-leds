import asyncio

from circuitpy_leds import Strip
from circuitpy_leds.support.color import wheel

# International Morse Code
MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.',
    ' ': ' ',  # Word separator
}


class MorseCode:
    """
    Scrolling morse code show that displays a text message encoded as morse code.

    Each word in the message is displayed in a different color from the color wheel.
    The message scrolls continuously across the LED strip.

    Spacing rules (default compact 1-3-1-2-4):
    - Dot = dot_length LEDs lit (default: 1)
    - Dash = dash_length LEDs lit (default: 3)
    - symbol_space LEDs between symbols within a letter (default: 1)
    - letter_space LEDs between letters (default: 2)
    - word_space LEDs between words (default: 4)
    """

    def __init__(self, strip: Strip, message: str = "HELLO", speed: float = 0.5, sleep_time: float = 0.05,
                 dot_length: int = 2, dash_length: int = 4, symbol_space: int = 2,
                 letter_space: int = 3, word_space: int = 5):
        """
        Initialize Morse Code scrolling show.

        :param strip: LED strip object
        :param message: Text message to encode and display (default: "HELLO")
        :param speed: Scroll speed in LEDs per frame (default: 0.5)
                      Higher = faster scrolling (e.g., 1.0 = 1 LED per frame)
                      Lower = slower scrolling (e.g., 0.1 = 0.1 LED per frame)
        :param sleep_time: Delay between frames in seconds (default: 0.05 for ~20 FPS)
        :param dot_length: Number of LEDs for a dot (default: 1)
        :param dash_length: Number of LEDs for a dash (default: 3)
        :param symbol_space: Number of LEDs between symbols in a letter (default: 1)
        :param letter_space: Number of LEDs between letters in a word (default: 2)
        :param word_space: Number of LEDs between words (default: 4)
        """
        self.strip = strip
        self.num_leds = len(strip)
        self.message = message.upper() if message else "HELLO"
        self.speed = speed
        self.sleep_time = sleep_time

        # Morse code spacing parameters
        self.dot_length = max(1, dot_length)  # Ensure at least 1
        self.dash_length = max(1, dash_length)
        self.symbol_space = max(0, symbol_space)  # Can be 0 for no space
        self.letter_space = max(0, letter_space)
        self.word_space = max(0, word_space)

        # Pre-compute the LED pattern for efficient scrolling
        self.pattern = self._build_pattern()
        self.pattern_length = len(self.pattern)

        # Ensure pattern has content
        if self.pattern_length == 0:
            # Fallback pattern if message encoding fails
            self.pattern = [(0, 0, 0)] * 10
            self.pattern_length = 10

    def _build_pattern(self):
        """
        Build the complete LED pattern from the message.

        :return: List of RGB tuples representing the complete scrolling pattern
        """
        words = self._get_valid_words()
        if not words:
            return []

        pattern = []
        colors = self._calculate_word_colors(len(words))

        for word_idx, word in enumerate(words):
            word_pattern = self._encode_word(word, colors[word_idx])
            pattern.extend(word_pattern)

            if self._should_add_word_space(word_idx, len(words)):
                pattern.extend(self._create_space(self.word_space))

        # Add padding at the end to create a visual gap before looping
        pattern.extend(self._create_space(10))

        return pattern

    def _get_valid_words(self):
        """Extract and filter non-empty words from the message."""
        return [word for word in self.message.split(' ') if word]

    def _calculate_word_colors(self, num_words):
        """Calculate colors for each word distributed around the color wheel."""
        color_step = 255 // num_words if num_words > 0 else 0
        return [wheel((idx * color_step) % 255) for idx in range(num_words)]

    def _encode_word(self, word, color):
        """
        Encode a single word into LED pattern.

        :param word: Word to encode
        :param color: RGB color tuple for this word
        :return: List of RGB tuples for the word
        """
        pattern = []
        for letter_idx, char in enumerate(word):
            letter_pattern = self._encode_letter(char, color)
            pattern.extend(letter_pattern)

            if self._should_add_letter_space(letter_idx, len(word)):
                pattern.extend(self._create_space(self.letter_space))

        return pattern

    def _encode_letter(self, char, color):
        """
        Encode a single letter into LED pattern.

        :param char: Character to encode
        :param color: RGB color tuple for this character
        :return: List of RGB tuples for the letter
        """
        morse = MORSE_CODE.get(char, '')
        if not morse:
            return []

        pattern = []
        for symbol_idx, symbol in enumerate(morse):
            pattern.extend(self._encode_symbol(symbol, color))

            if self._should_add_symbol_space(symbol_idx, len(morse)):
                pattern.extend(self._create_space(self.symbol_space))

        return pattern

    def _encode_symbol(self, symbol, color):
        """
        Encode a single morse symbol (dot or dash) into LED pattern.

        :param symbol: '.' or '-'
        :param color: RGB color tuple
        :return: List of RGB tuples for the symbol
        """
        if symbol == '.':
            return [color] * self.dot_length
        elif symbol == '-':
            return [color] * self.dash_length
        return []

    def _create_space(self, length):
        """Create a space (black LEDs) of specified length."""
        return [(0, 0, 0)] * length

    def _should_add_symbol_space(self, current_idx, total):
        """Check if space should be added after current symbol."""
        return current_idx < total - 1 and self.symbol_space > 0

    def _should_add_letter_space(self, current_idx, total):
        """Check if space should be added after current letter."""
        return current_idx < total - 1 and self.letter_space > 0

    def _should_add_word_space(self, current_idx, total):
        """Check if space should be added after current word."""
        return current_idx < total - 1 and self.word_space > 0

    async def execute(self, index: int):
        """
        Execute one frame of the scrolling morse code animation.

        :param index: Frame counter (increments each call)
        """
        if not self.pattern:
            # Safety check - should not happen with fallback in __init__
            self.strip.fill((0, 0, 0))
            self.strip.show()
            await asyncio.sleep(self.sleep_time)
            return

        # Calculate scroll offset based on index and speed
        offset = int(index * self.speed) % self.pattern_length

        # Map pattern to strip LEDs
        for i in range(self.num_leds):
            pattern_index = (offset + i) % self.pattern_length
            self.strip[i] = self.pattern[pattern_index]

        self.strip.show()
        await asyncio.sleep(self.sleep_time)

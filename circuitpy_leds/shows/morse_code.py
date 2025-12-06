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

    Spacing rules (compact 1-2-4):
    - Dot = 1 LED lit
    - Dash = 3 LEDs lit
    - 1 LED space between symbols within a letter
    - 2 LEDs space between letters
    - 4 LEDs space between words
    """

    def __init__(self, strip: Strip, message: str = "HELLO", speed: float = 0.5, sleep_time: float = 0.05):
        """
        Initialize Morse Code scrolling show.

        :param strip: LED strip object
        :param message: Text message to encode and display (default: "HELLO")
        :param speed: Scroll speed in LEDs per frame (default: 0.5)
                      Higher = faster scrolling (e.g., 1.0 = 1 LED per frame)
                      Lower = slower scrolling (e.g., 0.1 = 0.1 LED per frame)
        :param sleep_time: Delay between frames in seconds (default: 0.05 for ~20 FPS)
        """
        self.strip = strip
        self.num_leds = len(strip)
        self.message = message.upper() if message else "HELLO"
        self.speed = speed
        self.sleep_time = sleep_time

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
        pattern = []
        words = self.message.split(' ')

        # Filter out empty words (from multiple spaces)
        words = [w for w in words if w]

        if not words:
            return pattern

        num_words = len(words)

        # Calculate color spacing for even distribution around color wheel (0-254)
        color_step = 255 // num_words if num_words > 0 else 0

        for word_idx, word in enumerate(words):
            if not word:
                continue

            # Get color for this word from color wheel
            color_pos = (word_idx * color_step) % 255
            color = wheel(color_pos)

            # Encode each letter in the word
            for letter_idx, char in enumerate(word):
                morse = MORSE_CODE.get(char, '')

                if morse:
                    # Add dots and dashes
                    for symbol_idx, symbol in enumerate(morse):
                        if symbol == '.':
                            # Dot = 1 LED
                            pattern.append(color)
                        elif symbol == '-':
                            # Dash = 3 LEDs
                            pattern.extend([color, color, color])

                        # Add space between symbols (1 LED) - except after last symbol
                        if symbol_idx < len(morse) - 1:
                            pattern.append((0, 0, 0))

                    # Add space between letters (2 LEDs) - except after last letter
                    if letter_idx < len(word) - 1:
                        pattern.extend([(0, 0, 0), (0, 0, 0)])

            # Add space between words (4 LEDs) - except after last word
            if word_idx < num_words - 1:
                pattern.extend([(0, 0, 0)] * 4)

        # Add padding at the end to create a visual gap before looping
        pattern.extend([(0, 0, 0)] * 10)

        return pattern

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

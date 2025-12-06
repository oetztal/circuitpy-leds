"""
Conftest for show tests - mocks hardware dependencies
"""
import sys
from unittest.mock import MagicMock

# Mock CircuitPython hardware modules before any imports
sys.modules['board'] = MagicMock()
sys.modules['neopixel'] = MagicMock()
sys.modules['digitalio'] = MagicMock()
sys.modules['busio'] = MagicMock()

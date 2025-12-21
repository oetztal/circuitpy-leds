import pytest
import sys
from mock import patch, MagicMock


# Mock board module for non-CircuitPython environments
sys.modules['board'] = MagicMock()


@pytest.fixture
def mock_strip():
    with patch('circuitpy_leds.Strip') as strip:
        yield strip

@pytest.fixture
def mock_time_monotonic():
    with patch('time.monotonic') as time:
        yield time
import pytest
from mock import patch


@pytest.fixture
def mock_strip():
    with patch('circuitpy_leds.Strip') as strip:
        yield strip

@pytest.fixture
def mock_time_monotonic():
    with patch('time.monotonic') as time:
        yield time
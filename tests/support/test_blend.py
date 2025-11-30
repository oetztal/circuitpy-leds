import pytest
from mock import call

from circuitpy_leds.support.blend import SmoothBlend


@pytest.mark.parametrize(
    "delta_time,expected_value", [
        (0.0, 0),
        (1, 127.5),
        (2, 255),
        (3, 255),
    ]
)
def test_blend_one_led(mock_strip, mock_time_monotonic, delta_time, expected_value):
    start_time = 500.0
    mock_strip.__len__.return_value = 1
    mock_strip.__getitem__.return_value = (0, 0, 0)

    mock_time_monotonic.return_value = start_time

    blend = SmoothBlend(mock_strip, (255, 0, 0))

    mock_time_monotonic.return_value = start_time + delta_time

    blend.step()

    assert mock_strip.__setitem__.call_args_list == [
        call(0, (expected_value, 0, 0)),
    ]

def test_blend_two_leds(mock_strip, mock_time_monotonic):
    start_time = 500.0
    mock_strip.__len__.return_value = 2
    mock_strip.__getitem__.side_effect = [(0, 0, 0), (127,0,0)]

    mock_time_monotonic.return_value = start_time

    blend = SmoothBlend(mock_strip, (255, 0, 0))

    mock_time_monotonic.return_value = start_time + 1.0

    blend.step()

    assert mock_strip.__setitem__.call_args_list == [
        call(0, (127.5, 0, 0)),
        call(1, (191, 0, 0)),
    ]

def test_blend_two_leds_two_targets(mock_strip, mock_time_monotonic):
    start_time = 500.0
    mock_strip.__len__.return_value = 2
    mock_strip.__getitem__.side_effect = [(0, 0, 0), (255,0,0)]

    mock_time_monotonic.return_value = start_time

    blend = SmoothBlend(mock_strip, [(255, 0, 0), (0,0,0)])

    mock_time_monotonic.return_value = start_time + 1.0

    blend.step()

    assert mock_strip.__setitem__.call_args_list == [
        call(0, (127.5, 0, 0)),
        call(1, (127.5, 0, 0)),
    ]

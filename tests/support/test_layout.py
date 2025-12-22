import itertools
from unittest.mock import call

import pytest

from circuitpy_leds.support.layout import Layout


class TestPlainLayout:
    @pytest.fixture
    def plain_layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 0, False)

    def test_length(self, mock_strip, plain_layout):
        assert len(plain_layout) == 300

    def test_setitem(self, mock_strip, plain_layout):
        plain_layout[20] = (255, 0, 0)

        mock_strip.__setitem__.assert_called_once_with(20, (255, 0, 0))

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, plain_layout, index):
        with pytest.raises(IndexError):
            plain_layout[index] = (255, 0, 0)


class TestReversedPlainLayout:
    @pytest.fixture
    def plain_layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 0, False, True)

    def test_length(self, mock_strip, plain_layout):
        assert len(plain_layout) == 300

    def test_setitem(self, mock_strip, plain_layout):
        plain_layout[20] = (255, 0, 0)

        mock_strip.__setitem__.assert_called_once_with(279, (255, 0, 0))

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, plain_layout, index):
        with pytest.raises(IndexError):
            plain_layout[index] = (255, 0, 0)


class TestMirroredLayout:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 0, True)

    def test_length(self, mock_strip, layout):
        assert len(layout) == 150

    @pytest.mark.parametrize('index,expected_mirror', (
            (0, 299),
            (20, 279),
            (149, 150),
    ))
    def test_setitem(self, mock_strip, layout, index, expected_mirror):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(index, (255, 0, 0)),
            call(expected_mirror, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)


class TestMirroredReversedLayout:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 0, True, True)

    def test_length(self, mock_strip, layout):
        assert len(layout) == 150

    @pytest.mark.parametrize('index,expected,expected_mirror', (
            (0, 149, 150),
            (20, 129, 170),
            (149, 0, 299),
    ))
    def test_setitem(self, mock_strip, layout, index, expected, expected_mirror):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(expected, (255, 0, 0)),
            call(expected_mirror, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)


class TestMirroredLayoutWithDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        layout = Layout(mock_strip, 80, True)
        mock_strip.__setitem__.reset_mock()  # Reset after clearing dead LEDs
        return layout

    def test_switch_off_dead(self, mock_strip):
        mock_strip.__len__.return_value = 300
        Layout(mock_strip, 80, True)
        assert mock_strip.__setitem__.call_args_list == [call(index, (0, 0, 0)) for index in range(110, 190)]

    def test_length(self, layout):
        assert len(layout) == 110

    @pytest.mark.parametrize('index,expected_mirror', (
            (0, 299),
            (20, 279),
            (109, 190),
    ))
    def test_setitem(self, mock_strip, layout, index,
                     expected_mirror):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(index, (255, 0, 0)),
            call(expected_mirror, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 110))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)


class TestMirroredLayoutWithNegativeDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        layout = Layout(mock_strip, -80, True)
        mock_strip.__setitem__.reset_mock()  # Reset after clearing dead LEDs
        return layout

    def test_switch_off_dead(self, mock_strip):
        mock_strip.__len__.return_value = 300
        Layout(mock_strip, -80, True)
        assert mock_strip.__setitem__.call_args_list == list(itertools.chain.from_iterable([
            [call(index, (0, 0, 0)),call(110 - index, (0,0,0))] for index in range(0, 40)]))

    def test_length(self, layout):
        assert len(layout) == 110

    @pytest.mark.parametrize('index,expected_index,expected_mirror', (
            (0, 40, 259),
            (20, 60, 239),
            (109, 149, 150),
    ))
    def test_setitem(self, mock_strip, layout, index,
                     expected_index, expected_mirror):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(expected_index, (255, 0, 0)),
            call(expected_mirror, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 110))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)


class TestPlainLayoutWithDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        layout = Layout(mock_strip, 80, False)
        mock_strip.__setitem__.reset_mock()  # Reset after clearing dead LEDs
        return layout

    def test_length(self, mock_strip, layout):
        assert len(layout) == 220

    @pytest.mark.parametrize('index,expected_index', (
            (0, 80),
            (219, 299),
    ))
    def test_setitem(self, mock_strip, layout, index, expected_index):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(expected_index, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 220))
    def test_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)


class TestPlainLayoutWithNegativeDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        layout = Layout(mock_strip, -80, False)
        mock_strip.__setitem__.reset_mock()  # Reset after clearing dead LEDs
        return layout

    def test_length(self, mock_strip, layout):
        assert len(layout) == 220

    @pytest.mark.parametrize('index, expected_index', (
            (0, 0),
            (219, 219),
    ))
    def test_setitem(self, mock_strip, layout, index,
                     expected_index):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(expected_index, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 220))
    def test_index_error(self, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)

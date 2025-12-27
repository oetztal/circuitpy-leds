from unittest.mock import call

import pytest

from circuitpy_leds.support.layout import Layout


class TestPlainLayout:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 0, False)

    def test_length(self, mock_strip, layout):
        assert len(layout) == 300

    def test_setitem(self, mock_strip, layout):
        layout[20] = (255, 0, 0)

        mock_strip.__setitem__.assert_called_once_with(20, (255, 0, 0))

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)

    def test_repr(self, layout):
        assert str(layout) == "<Layout default>"


class TestReversedPlainLayout:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 0, False, True)

    def test_length(self, mock_strip, layout):
        assert len(layout) == 300

    def test_setitem(self, mock_strip, layout):
        layout[20] = (255, 0, 0)

        mock_strip.__setitem__.assert_called_once_with(279, (255, 0, 0))

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)

    def test_repr(self, layout):
        assert str(layout) == "<Layout reverse>"


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

    def test_repr(self, layout):
        assert str(layout) == "<Layout mirror>"


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
    def test_setitem(self, mock_strip, layout, index, expected,expected_mirror):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(expected, (255, 0, 0)),
            call(expected_mirror, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 300))
    def test_setitem_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)

    def test_repr(self, layout):
        assert str(layout) == "<Layout mirror, reverse>"


class TestMirroredLayoutWithDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 80, True)

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

    def test_repr(self, layout):
        assert str(layout) == "<Layout mirror, dead=80>"


class TestPlainLayoutWithDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, 80, False)

    def test_length(self, mock_strip, layout):
        assert len(layout) == 220

    @pytest.mark.parametrize('index', (
            (0),
            (219),
    ))
    def test_setitem(self, mock_strip, layout, index):
        layout[index] = (255, 0, 0)

        assert mock_strip.__setitem__.call_args_list == [
            call(index, (255, 0, 0)),
        ]

    @pytest.mark.parametrize('index', (-1, 220))
    def test_index_error(self, mock_strip, layout, index):
        with pytest.raises(IndexError):
            layout[index] = (255, 0, 0)

    def test_repr(self, layout):
        assert str(layout) == "<Layout dead=80>"



class TestPlainLayoutWithNegativeDeadLEDs:
    @pytest.fixture
    def layout(self, mock_strip):
        mock_strip.__len__.return_value = 300
        return Layout(mock_strip, -80, False)

    def test_length(self, mock_strip, layout):
        assert len(layout) == 220

    @pytest.mark.parametrize('index, expected_index', (
            (0, 80),
            (219, 299),
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

    def test_repr(self, layout):
        assert str(layout) == "<Layout dead=-80>"


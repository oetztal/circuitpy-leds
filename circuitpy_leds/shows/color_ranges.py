import asyncio
import math

from .. import Strip
from ..support.blend import SmoothBlend


class ColorRanges:
    """
    Display solid color ranges across the LED strip with sharp transitions.

    Perfect for visualizing flags with 2-3 color sections or creating custom
    multi-color patterns.

    Examples:
        # German flag (equal thirds)
        ColorRanges(strip, colors=[(0, 0, 0), (255, 0, 0), (255, 215, 0)])

        # French flag (equal thirds)
        ColorRanges(strip, colors=[(0, 85, 164), (255, 255, 255), (239, 65, 53)])

        # Custom racing stripes (30% red, 40% white, 30% blue)
        # Boundary points at 30% and 70%
        ColorRanges(strip, colors=[(255, 0, 0), (255, 255, 255), (0, 0, 255)], ranges=[30, 70])
    """

    def __init__(self, strip: Strip, colors: list[list[int]], ranges: list[float] = None):
        """
        Initialize ColorRanges effect.

        :param strip: LED strip object
        :param colors: List of RGB color tuples (required)
        :param ranges: Optional list of boundary percentages (length = len(colors) - 1)
                      If not provided, colors are distributed equally
        :raises ValueError: If validation fails

        Example:
            colors=[(255,0,0), (255,255,255), (0,0,255)], ranges=[40, 60]
            Results in: Red (0-40%), White (40-60%), Blue (60-100%)
        """
        self.strip = strip
        self.num_leds = len(strip)

        # Validate and store colors
        self.colors = self._validate_colors(colors)

        # Build internal ranges format: [(start_pct, end_pct, color), ...]
        if ranges is None or len(ranges) == 0:
            # Equal distribution
            self.ranges = self._build_equal_ranges(self.colors)
        else:
            # Custom distribution with boundary points
            self._validate_boundary_ranges(ranges, len(self.colors))
            self.ranges = self._build_ranges_from_boundaries(self.colors, ranges)

        # Pre-compute per-LED colors for sharp transitions
        self.target_colors = self._compute_led_colors()
        self.blend = None

    def _validate_colors(self, colors: list[list[int]]) -> list[tuple]:
        """
        Validate color list.

        :param colors: List of RGB color tuples
        :return: Validated colors list
        :raises ValueError: If colors list is invalid
        """
        if not colors:
            raise ValueError("Colors list cannot be empty")

        # Validate color tuples
        for color in colors:
            if not isinstance(color, list) or len(color) != 3:
                raise ValueError(f"Color must be RGB tuple (r, g, b), got {color}")
            if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                raise ValueError(f"Color values must be integers 0-255, got {color}")

        return [tuple(color) for color in colors]

    def _validate_boundary_ranges(self, ranges: list[float], num_colors: int):
        """
        Validate boundary ranges list.

        :param ranges: List of boundary percentages
        :param num_colors: Number of colors
        :raises ValueError: If ranges list is invalid
        """
        expected_length = num_colors - 1

        if len(ranges) != expected_length:
            raise ValueError(
                f"Ranges list must have {expected_length} elements (one less than colors), "
                f"got {len(ranges)} elements"
            )

        # Validate all boundaries are numbers between 0 and 100
        for i, boundary in enumerate(ranges):
            if not isinstance(boundary, (int, float)):
                raise ValueError(f"Boundary at index {i} must be a number, got {type(boundary)}")
            if not 0 < boundary < 100:
                raise ValueError(f"Boundary at index {i} must be between 0 and 100, got {boundary}")

        # Validate boundaries are in ascending order
        for i in range(len(ranges) - 1):
            if ranges[i] >= ranges[i + 1]:
                raise ValueError(
                    f"Boundaries must be in ascending order: {ranges[i]} >= {ranges[i + 1]}"
                )

    def _build_equal_ranges(self, colors: list[tuple]) -> list[tuple]:
        """
        Build ranges with equal distribution of colors.

        :param colors: List of RGB color tuples
        :return: List of (start_pct, end_pct, color) tuples
        """
        num_colors = len(colors)
        pct_per_color = 100.0 / num_colors

        ranges = []
        for i, color in enumerate(colors):
            start_pct = i * pct_per_color
            # Ensure last range ends exactly at 100 to avoid floating point issues
            end_pct = 100.0 if i == num_colors - 1 else (i + 1) * pct_per_color
            ranges.append((start_pct, end_pct, color))

        return ranges

    def _build_ranges_from_boundaries(self, colors: list[tuple], boundaries: list[float]) -> list[tuple]:
        """
        Build ranges from colors and boundary points.

        :param colors: List of RGB color tuples
        :param boundaries: List of boundary percentages (length = len(colors) - 1)
        :return: List of (start_pct, end_pct, color) tuples

        Example:
            colors=[(255,0,0), (255,255,255), (0,0,255)], boundaries=[40, 60]
            Returns: [(0, 40, (255,0,0)), (40, 60, (255,255,255)), (60, 100, (0,0,255))]
        """
        ranges = []

        for i, color in enumerate(colors):
            # First range starts at 0
            start_pct = 0.0 if i == 0 else boundaries[i - 1]

            # Last range ends at 100
            end_pct = 100.0 if i == len(colors) - 1 else boundaries[i]

            ranges.append((start_pct, end_pct, color))

        return ranges

    def _compute_led_colors(self) -> list[tuple]:
        """
        Compute per-LED colors from percentage ranges with sharp transitions.

        Algorithm:
        - Convert percentage ranges to LED index ranges
        - For each LED, find which range it belongs to based on index
        - This avoids floating point comparison issues

        :return: List of RGB color tuples, one per LED
        """
        # Special case: single LED gets first color
        if self.num_leds == 1:
            return [self.ranges[0][2]]

        led_colors = [(0,0,0)] * self.num_leds

        # Convert percentage ranges to LED index ranges and assign colors
        for start_pct, end_pct, color in self.ranges:
            # Convert percentages to LED indices
            # start_idx is inclusive, end_idx is exclusive
            start_idx = int((start_pct / 100.0) * self.num_leds)
            end_idx = int((end_pct / 100.0) * self.num_leds)

            # Handle the last range specially to ensure it includes the final LED
            if math.isclose(end_pct, 100.0, rel_tol=1e-06, abs_tol=1e-06):
                end_idx = self.num_leds

            # Assign this color to all LEDs in this range
            for led_idx in range(start_idx, end_idx):
                led_colors[led_idx] = color

        return led_colors

    async def execute(self, _):
        """
        Execute one frame of the color ranges effect.

        On first call, creates a SmoothBlend with pre-computed colors.
        Subsequent calls step the blend animation until complete.

        :param index: Frame counter (not used for static display)
        """
        if self.blend is None:
            self.blend = SmoothBlend(self.strip, self.target_colors)

        self.blend.step()

        await asyncio.sleep(0.025)

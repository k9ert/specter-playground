"""Line -- reusable two-point LVGL line widget."""

import lvgl as lv

from ..theming import apply_style
from ..utils import set_size


class Line(lv.line):
    """Draw a styled two-point line that fills its parent."""

    def __init__(self, parent, x1, y1, x2, y2, style=None):
        super().__init__(parent)
        self._points = [
            lv.point_precise_t({"x": x1, "y": y1}),
            lv.point_precise_t({"x": x2, "y": y2}),
        ]
        self.set_points(self._points, len(self._points))
        set_size(self, lv.pct(100), lv.pct(100))
        if style is not None:
            apply_style(self, style)
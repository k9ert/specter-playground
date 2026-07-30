"""UI Explainer component for guided tours / onboarding.

Provides a spotlight/coach-mark style overlay that highlights a UI element
and displays explanatory text with navigation controls.
"""

import lvgl as lv

from ..utils import (
    get_size, set_size, set_pos
)
from ..symbol_lib import BTC_ICONS
from ..templates.specter_gui_base import SpecterGuiMixin
from ..theming import apply_style
from ..widgets import MenuItem, modal_overlay, button_modal


class UIExplainer(SpecterGuiMixin):
    """
    A spotlight-style explainer that highlights a UI element with a dimmed overlay
    and displays explanatory text with navigation buttons.
    
    Controlled by a parent GuidedTour that manages navigation between steps.
    
    Args:
        tour: Parent GuidedTour instance that controls navigation
        highlighted_element: lv.obj to highlight, OR tuple (x, y, width, height) for manual positioning, or None
        text: Explanation text to display
        text_position: Position of text box - "center" (default), "above", "below", "left", "right"
    """
    
    def __init__(self, tour, highlighted_element, text, text_position="center"):
        self.tour = tour
        self.highlighted_element = highlighted_element
        self.text = text
        self.text_position = text_position
        
        # LVGL objects (created on show())
        self._overlay = None
        self._dim_strips = []
        self._modal_box = None
    
    def show(self):
        """Create and display the explainer overlay."""
        cutout = self._get_cutout_area()
        self._overlay = modal_overlay()
        #make transparent as we will add our own dim strips on top
        apply_style(self._overlay, "APPEARANCE.TRANSPARENT")
        self._create_dim_strips(cutout)
        self._create_text_box()
    
    def hide(self):
        """Remove and destroy all LVGL objects."""
        if self._overlay is not None:
            self._overlay.delete()
            self._overlay = None
        self._dim_strips = []
        self._modal_box = None
    
    def _get_cutout_area(self):
        """
        Calculate the cutout area (x, y, width, height).
        
        Returns:
            tuple: (x, y, width, height) in screen coordinates, or None if no element
        """
        if self.highlighted_element is None:
            # No element to highlight - full overlay
            return None
        else:
            # Get absolute screen coordinates from lv.obj via get_coords()
            # (LVGL 9.x: area.x1/y1 are absolute screen coordinates)
            obj = self.highlighted_element
            coords = lv.area_t()
            obj.get_coords(coords)
            x = coords.x1
            y = coords.y1
            width, height = get_size(obj)
            return (x, y, width, height)
    
    def _create_dim_strips(self, cutout):
        """
        Create the semi-transparent overlay around the cutout (or full overlay if no cutout).
        
        Layout with cutout:
        ┌─────────────────────────────────────┐
        │       TOP STRIP (dimmed)            │
        ├─────┬──────────────────┬────────────┤
        │LEFT │    CUTOUT        │   RIGHT    │
        │DIM  │  (transparent)   │   DIM      │
        ├─────┴──────────────────┴────────────┤
        │       BOTTOM STRIP (dimmed)         │
        └─────────────────────────────────────┘
        
        If cutout is None, creates a single full-screen dim overlay.
        """
        screen_width, screen_height = get_size(self.gui)

        def add_strip(x, y, w, h):
            """Create a dim strip at the given position and size."""
            strip = lv.obj(self._overlay)
            set_pos(strip, x, y)
            set_size(strip, w, h)
            apply_style(strip, ["WIDGET.OVERLAY"])
            self._dim_strips.append(strip)

        if cutout is None:
            # Full-screen dim overlay
            add_strip(0, 0, screen_width, screen_height)
        else:
            cut_x, cut_y, cut_w, cut_h = cutout
            # Top strip
            if cut_y > 0:
                add_strip(0, 0, screen_width, cut_y)
            # Bottom strip
            bottom_y = cut_y + cut_h
            if bottom_y < screen_height:
                add_strip(0, bottom_y, screen_width, screen_height - bottom_y)
            # Left strip
            if cut_x > 0:
                add_strip(0, cut_y, cut_x, cut_h)
            # Right strip
            right_x = cut_x + cut_w
            if right_x < screen_width:
                add_strip(right_x, cut_y, screen_width - right_x, cut_h)
    
    def _create_text_box(self):
        """Create the text box with explanation and navigation buttons. This is
        a special case of button_modal(): we own the overlay/backdrop (spotlight
        dim strips) and positioning (align_to), so it's passed in as `parent`,
        and auto_close is disabled since the tour controls the modal's lifecycle
        via hide().
        """
        is_first = self.tour.is_first()
        is_last = self.tour.is_last()

        prev_spec = MenuItem(icon=BTC_ICONS.CARET_LEFT,
                             target=lambda: self.tour.prev(),
                             visible=not is_first)

        if is_last:
            skip_spec = MenuItem(icon=BTC_ICONS.CHECK,
                                 target=lambda: self.tour.skip(),
                                 modifier="Highlight")
        else:
            skip_spec = MenuItem(text=self.t("TOUR_SKIP_BTN"),
                                 target=lambda: self.tour.skip())

        next_spec = MenuItem(icon=BTC_ICONS.CARET_RIGHT,
                             target=lambda: self.tour.next(),
                             visible=not is_last,
                             modifier="Highlight" if not is_last else None)

        overlay = button_modal(
            self.text,
            buttons=[prev_spec, skip_spec, next_spec],
            auto_close=False,
            parent=self._overlay,
        )
        self._modal_box = overlay.modal_window

        align_enum = lv.ALIGN.CENTER
        if self.text_position == "left":
            align_enum = lv.ALIGN.OUT_LEFT_MID
        elif self.text_position == "right":
            align_enum = lv.ALIGN.OUT_RIGHT_MID
        elif self.text_position == "above":
            align_enum = lv.ALIGN.OUT_TOP_MID
        elif self.text_position == "below":
            align_enum = lv.ALIGN.OUT_BOTTOM_MID

        self._modal_box.align_to(self.highlighted_element, align_enum, 0, 0)


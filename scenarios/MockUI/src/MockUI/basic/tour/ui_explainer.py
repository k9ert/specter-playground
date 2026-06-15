"""UI Explainer component for guided tours / onboarding.

Provides a spotlight/coach-mark style overlay that highlights a UI element
and displays explanatory text with navigation controls.
"""

import lvgl as lv

from ..utils import (
    EXPLAINER_WIDTH,
    EXPLAINER_HEIGHT,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    get_size, set_size, set_pos, set_scroll
)
from ..symbol_lib import BTC_ICONS
from ..templates.specter_gui_base import SpecterGuiMixin
from ..theming import apply_style
from ..widgets import Btn, flex_row, flex_col, flex_container, body_label, modal_overlay


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
        self._text_box = None
    
    def show(self):
        """Create and display the explainer overlay."""
        cutout = self._get_cutout_area()
        self._overlay = modal_overlay()
        # don't use invisible as this will also make all content on top
        # (cutouts, text box) invisible
        apply_style(self._overlay, ["APPEARANCE.TRANSPARENT"])
        self._create_dim_strips(cutout)
        self._create_text_box(*self._calculate_text_box_position(cutout))
    
    def hide(self):
        """Remove and destroy all LVGL objects."""
        if self._overlay is not None:
            self._overlay.delete()
            self._overlay = None
        self._dim_strips = []
        self._text_box = None
    
    def _get_cutout_area(self):
        """
        Calculate the cutout area (x, y, width, height).
        
        Returns:
            tuple: (x, y, width, height) in screen coordinates, or None if no element
        """
        if self.highlighted_element is None:
            # No element to highlight - full overlay
            return None
        elif isinstance(self.highlighted_element, tuple):
            # Manual positioning
            return self.highlighted_element
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
        screen_width = SCREEN_WIDTH
        screen_height = SCREEN_HEIGHT

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
    
    def _create_text_box(self, box_x, box_y, box_width, box_height):
        """Create the text box with explanation and navigation buttons.
        
        Args:
            box_x: X position for the text box
            box_y: Y position for the text box
            box_width: Width of the text box
            box_height: Height of the text box
        """
        # Create text box container
        self._text_box = flex_container(self._overlay,
                                        width=box_width, height=box_height,
                                        main_align=lv.FLEX_ALIGN.SPACE_BETWEEN,
                                        scrollable=False)
        set_pos(self._text_box, box_x, box_y)
        apply_style(self._text_box, ["WIDGET.MODAL_WINDOW"])
        
        # Create text label (with flex grow to take available space)
        self.text_container = flex_col(self._text_box, width=lv.pct(100))
        self.text_container.set_flex_grow(1)
        set_scroll(self.text_container, horizontal=False, vertical=False)
        
        self.text_label = body_label(self.text_container, self.text)
        self.text_label.center()
        
        # Create navigation button container
        self.nav_container = flex_row(self._text_box, height=60)
        set_scroll(self.nav_container, horizontal=False, vertical=False)
        
        # Get position info from tour
        is_first = self.tour.is_first()
        is_last = self.tour.is_last()
        
        # Previous button (or invisible placeholder on first screen)
        self.PrevBtn = Btn(self.nav_container, 
                           icon=BTC_ICONS.CARET_LEFT, 
                           size=(60, 50),
                           callback=self._on_prev_clicked)

        if is_first:
            apply_style(self.PrevBtn, "APPEARANCE.INVISIBLE")
        
        # Skip/Complete button (always present)
        if is_last:
            self.SkipBtn = Btn(self.nav_container, 
                               icon=BTC_ICONS.CHECK, 
                               size=(60, 50),
                               callback=self._on_skip_clicked)
        else:
            self.SkipBtn = Btn(self.nav_container, 
                               text=self.t("TOUR_SKIP_BTN"),
                               size=(160, 50),
                               callback=self._on_skip_clicked)
        
        # Next button (or invisible placeholder on last screen)
        self.NextBtn = Btn(self.nav_container,
                           icon=BTC_ICONS.CARET_RIGHT, 
                           size=(60, 50),
                           callback=self._on_next_clicked)
        if is_last:
            apply_style(self.NextBtn, "APPEARANCE.INVISIBLE")
    
    def _calculate_text_box_position(self, cutout):
        """Calculate text box dimensions and position based on text_position setting and cutout.
        
        Args:
            cutout: Tuple (x, y, w, h) of cutout area, or None for full overlay
            
        Returns:
            tuple: (x, y, width, height) for the text box
        """
        disp = lv.display_get_default()
        screen_width = disp.get_horizontal_resolution()
        screen_height = disp.get_vertical_resolution()
        
        # Calculate box dimensions
        box_width = EXPLAINER_WIDTH
        box_height = EXPLAINER_HEIGHT
        
        # Center position (used as default and when no cutout)
        center_x = (screen_width - box_width) // 2
        center_y = (screen_height - box_height) // 2
        
        # If no cutout or center position requested, return centered
        if cutout is None or self.text_position == "center" or self.text_position not in ("above", "below", "left", "right"):
            return (center_x, center_y, box_width, box_height)
        
        cut_x, cut_y, cut_w, cut_h = cutout
        margin = 10  # Margin from cutout/screen edges
        
        if self.text_position == "above":
            # Above the cutout, centered horizontally
            x = center_x
            y = cut_y - box_height - margin
            # Ensure it stays on screen
            if y < margin:
                y = margin
        elif self.text_position == "below":
            # Below the cutout, centered horizontally
            x = center_x
            y = cut_y + cut_h + margin
            # Ensure it stays on screen
            if y + box_height > screen_height - margin:
                y = screen_height - box_height - margin
        elif self.text_position == "left":
            # Left of the cutout, centered vertically
            x = cut_x - box_width - margin
            y = center_y
            # Ensure it stays on screen
            if x < margin:
                x = margin
        elif self.text_position == "right":
            # Right of the cutout, centered vertically
            x = cut_x + cut_w + margin
            y = center_y
            # Ensure it stays on screen
            if x + box_width > screen_width - margin:
                x = screen_width - box_width - margin
        
        return (x, y, box_width, box_height)
    
    def _on_prev_clicked(self, e):
        """Handle previous button click - delegate to tour."""
        if e.get_code() == lv.EVENT.CLICKED:
            self.tour.prev()
    
    def _on_next_clicked(self, e):
        """Handle next button click - delegate to tour."""
        if e.get_code() == lv.EVENT.CLICKED:
            self.tour.next()
    
    def _on_skip_clicked(self, e):
        """Handle skip/complete button click - delegate to tour."""
        if e.get_code() == lv.EVENT.CLICKED:
            self.tour.skip()

"""UI Explainer component for guided tours / onboarding.

Provides a spotlight/coach-mark style overlay that highlights a UI element
and displays explanatory text with navigation controls.
"""

import lvgl as lv
from ..utils.ui_consts import (
    EXPLAINER_WIDTH_PCT,
    EXPLAINER_HEIGHT_PCT,
    DEFAULT_MODAL_BG_OPA,
    BLACK_HEX,
)
from ..symbol_lib import BTC_ICONS
from ..widgets.modal_overlay import ModalOverlay
from ..widgets import Btn, flex_row, flex_col, body_label, dialog_card


class UIExplainer:
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
        self._modal = None
        self._overlay = None  # alias for self._modal.overlay, used internally
        self._dim_strips = []
        self._text_box = None
    
    def show(self):
        """Create and display the explainer overlay."""
        cutout = self._get_cutout_area()
        self._modal = ModalOverlay(bg_opa=lv.OPA.TRANSP)
        self._overlay = self._modal.overlay
        self._create_dim_strips(cutout)
        self._create_text_box(*self._calculate_text_box_position(cutout))
    
    def hide(self):
        """Remove and destroy all LVGL objects."""
        if self._modal is not None:
            self._modal.close()
            self._modal = None
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
            width = obj.get_width()
            height = obj.get_height()
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
        disp = lv.display_get_default()
        screen_width = disp.get_horizontal_resolution()
        screen_height = disp.get_vertical_resolution()

        def add_strip(x, y, w, h):
            """Create a dim strip at the given position and size."""
            strip = lv.obj(self._overlay)
            strip.set_pos(x, y)
            strip.set_size(w, h)
            strip.set_style_bg_color(BLACK_HEX, 0)
            strip.set_style_bg_opa(DEFAULT_MODAL_BG_OPA, 0)
            strip.set_style_border_width(0, 0)
            strip.set_style_pad_all(0, 0)
            strip.set_style_radius(0, 0)
            strip.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
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
        self._text_box = dialog_card(self._overlay, box_width, box_height, box_x, box_y, pad=10)
        self._text_box.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        
        # Create text label (with flex grow to take available space)
        text_container = flex_col(self._text_box, width=lv.pct(100))
        text_container.set_flex_grow(1)
        text_container.set_style_pad_all(5, 0)
        text_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        
        text_label = body_label(text_container, self.text)
        text_label.center()
        
        # Create navigation button container
        nav_container = flex_row(self._text_box, height=60, pad=0)
        nav_container.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
        
        # Get position info from tour
        is_first = self.tour.is_first()
        is_last = self.tour.is_last()
        
        # Previous button (or invisible placeholder on first screen)
        PrevBtn = Btn(nav_container, icon=BTC_ICONS.CARET_LEFT, size=(60, 50),
            callback=self._on_prev_clicked)
        PrevBtn.set_visible(not is_first)
        
        # Skip/Complete button (always present)
        if is_last:
            Btn(nav_container, icon=BTC_ICONS.CHECK, size=(60, 50),
                callback=self._on_skip_clicked)
        else:
            Btn(nav_container, text=self.tour.nav.i18n.t("TOUR_SKIP_BTN"),
                size=(160, 50), callback=self._on_skip_clicked)
        
        # Next button (or invisible placeholder on last screen)
        NextBtn = Btn(nav_container, icon=BTC_ICONS.CARET_RIGHT, size=(60, 50),
            callback=self._on_next_clicked)
        NextBtn.set_visible(not is_last)
    
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
        box_width = int(screen_width * EXPLAINER_WIDTH_PCT / 100)
        box_height = int(screen_height * EXPLAINER_HEIGHT_PCT / 100)
        
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

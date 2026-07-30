"""DropUp — abstract base class for bottom-sheet selection overlays.

Public API (used by NavigationBar):
  dropup.get_state()       → DropUpState constant
  dropup.open(container)  → build and show the panel inside *container*
  dropup.close()          → animate panel out; fires _on_closed when done
  dropup.refresh()        → rebuild card list (called after state changes)

The panel fills from the nav bar top edge upward.
"""

import lvgl as lv
from micropython import const

from .specter_gui_base import SpecterGuiMixin, SpecterGuiElement
from ..widgets import Btn
from ..utils import (
    slide_y, delete_all_children_of,
    set_pos, set_scroll, set_propagate_events,
    get_size, get_pos,
)
from ..symbol_lib import BTC_ICONS
from ..theming import apply_style


class DropUpState:
    """Valid states for a ``DropUp`` instance."""
    CLOSED  = const(0)
    OPENING = const(1)
    OPEN    = const(2)
    CLOSING = const(3)


class DropUp(SpecterGuiMixin):
    """Abstract base for drop-up overlays.

    Subclasses must implement the four abstract
    methods: ``_get_items``, ``_build_card``, ``_navigate_add``,
    ``_add_button_label``.
    """

    def __init__(self):
        self._panel = None       # lv.obj panel widget when open
        self._backdrop = None    # backdrop overlay the panel is parented to when open
        self._on_closed = None   # callback()/None — called after close animation
        self._animating = False
        self._closing = False    # True while close animation is running
        self._anim = None

    # ── Public API ────────────────────────────────────────────────────────────

    def get_state(self):
        """Return the current drop-up state as a ``DropUpState`` constant."""
        if self._panel is None:
            return DropUpState.CLOSED
        if self._animating:
            return DropUpState.CLOSING if self._closing else DropUpState.OPENING
        return DropUpState.OPEN

    def open(self, backdrop_overlay):
        """Build and slide in the panel inside *backdrop_overlay*."""
        state = self.get_state()
        if state in (DropUpState.OPENING, DropUpState.CLOSING, DropUpState.OPEN):
            return state

        self._backdrop = backdrop_overlay
        self._panel = SpecterGuiElement(backdrop_overlay)
        apply_style(self._panel, "CONTAINER.DROPUP")
        set_scroll(self._panel, horizontal=False, vertical=True)
        set_propagate_events(self._panel, False)

        self._fill_panel()

        # ── Slide-in animation ────────────────────────────────────────────────
        if self.ui_state.are_animations_enabled:
            self._animating = True

            def _on_open_done(anim):
                self._animating = False
                self._anim = None

            #needed to finish the flex layout
            self._panel.update_layout() 
            max_h = self._backdrop.get_height()
            pan_w, pan_h = get_size(self._panel)
            panel_y = max_h - pan_h
            self._anim = slide_y(self._panel, max_h, panel_y, on_done_cb=_on_open_done)
            self._anim.start()

        return self.get_state()

    def close(self):
        """Slide the panel out; calls ``_on_closed`` when animation finishes."""
        state = self.get_state()
        if state in (DropUpState.OPENING, DropUpState.CLOSING, DropUpState.CLOSED):
            return state  # animation in progress or already closed, do nothing

        def _on_close_done(anim):
            self._animating = False
            self._closing = False
            self._anim = None
            if self._panel is not None:
                self._panel.delete()
            self._panel = None
            self._backdrop = None
            if self._on_closed is not None:
                self._on_closed()

        if self.ui_state.are_animations_enabled:
            self._animating = True
            self._closing = True
            panel_x_now, panel_y_now = get_pos(self._panel)
            panel_y_end = self._backdrop.get_height()  # slide off-screen down
            self._anim = slide_y(self._panel, panel_y_now, panel_y_end, on_done_cb=_on_close_done)
            self._anim.start()
        else:
            _on_close_done(None)

        return self.get_state()

    def refresh(self):
        """Rebuild cards in place (called after state changes)."""
        if self.get_state() != DropUpState.OPEN:
            return
        self._fill_panel()

    def cancel_animation(self):
        """Discard any in-flight open/close animation without running its callback.
        """
        self._anim = None
        self._animating = False
        self._closing = False

    # ── Internal build ────────────────────────────────────────────────────────

    def _fill_panel(self):
        """Clear, repopulate, and resize/reposition the panel."""
        delete_all_children_of(self._panel)

        self._panel.rows = []
        for item in self._get_items():
            #styling is done in _build_card
            row = self._build_card(self._panel, item)
            apply_style(row, "CONTAINER.DROP_UP_ROW")
            self._panel.rows.append(row)

        # Add button row
        row = SpecterGuiElement(self._panel)
        apply_style(row, "CONTAINER.DROP_UP_ROW")
        self._panel.rows.append(row)

        self._add_button = Btn(
            row,
            icon=BTC_ICONS.PLUS,
            text=self._add_button_label(),
            callback=self._add_cb,
            background_style="WIDGET.DROP_UP_ADDBTN",
            foreground_style="WIDGET.DROP_UP_ADDBTN_FG",
        )
        self._panel.update_layout()
        w, h = get_size(self._panel)
        set_pos(self._panel, 0, max(self._backdrop.get_height() - h, 0))

    def _add_cb(self):
        self.close()
        self._navigate_add()

    def _make_on_row_click_cb(self, item, ctx, attr, setter, nav_target, nav_kwarg):
        """Row click handler: close, then switch active item or navigate."""
        def _cb(e):
            self.close()
            if (self.context == ctx
                    and getattr(self.ui_state, attr) is not None):
                getattr(self.ui_state, setter)(item)
                self.gui.refresh_ui()
            else:
                self.on_navigate(nav_target, **{nav_kwarg: item})

        return _cb

    # ── Abstract interface ────────────────────────────────────────────────────

    def _get_items(self):
        """Return list of items (seeds or wallets) to display."""
        raise NotImplementedError

    def _build_card(self, parent, item):
        """Build one item card inside *parent* and return the row widget."""
        raise NotImplementedError

    def _navigate_add(self):
        """Navigate to the add-item screen."""
        raise NotImplementedError

    def _add_button_label(self):
        """Return text for the add button."""
        raise NotImplementedError

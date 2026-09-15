"""DropUp — abstract base class for bottom-sheet selection overlays.

Public API (used by NavigationBar):
  dropup.get_state()      → DropUpState constant
  dropup.open(container)  → build and show the panel inside *container*
  dropup.close()          → animate panel out; fires _on_closed when done
  dropup.refresh()        → rebuild card list (called after state changes)

The panel fills from the nav bar top edge upward.
"""

import lvgl as lv
from micropython import const

from .specter_gui_base import SpecterGuiMixin, SpecterGuiElement
from ..widgets import Btn, InfoCard, TreeList
from ..utils import (
    build_forest,
    slide_y, delete_all_children_of,
    set_size, set_pos, set_scroll, set_propagate_events,
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
    """Base class for bottom-sheet DropUp panels. A DropUp panel contains a list of
    selectable items, each of which is presented in a card-like interface.
    There can be hierarchical relationships among items, so the panel supports
    tree-like data item structure with expansion and collapse behavior.

    This base class owns the panel lifecycle, generic tree construction, expansion
    state, rendering, and shared card sizing.
    Subclasses own domain data, hierarchy rules, card content, and item actions.

    This keeps the generic look and feel consistent across different DropUp panels,
    while allowing each subclass to define its own data model and detailed item
    behavior.

    Subclasses must provide
        - ``_get_selectable_items``
        - ``EXPANSION_CONTEXT``
        - ``_delete_from_gui``
        - ``_build_card``
        - ``_add_button_label``
        - ``_navigate_add``.
    They may provide
        - ``_get_item_children`` or ``_get_item_parent`` to define a hierarchy, and
        - ``_get_item_key`` when the item itself is not a stable unique key.
    """

    EXPANSION_CONTEXT = None
    _get_item_parent = None
    _get_item_children = None
    _get_item_key = None

    def __init__(self):
        self._panel = None       # lv.obj panel widget when open
        self._backdrop = None    # backdrop overlay the panel is parented to when open
        self._on_closed = None   # callback()/None — called after close animation
        self._animating = False
        self._closing = False    # True while close animation is running
        self._anim = None
        self._item_list = None

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
            _, max_h = get_size(self._backdrop)
            _, pan_h = get_size(self._panel)
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
            _, panel_y_now = get_pos(self._panel)
            _, panel_y_end = get_size(self._backdrop)  # slide off-screen down
            self._anim = slide_y(self._panel, panel_y_now, panel_y_end, on_done_cb=_on_close_done)
            self._anim.start()
        else:
            _on_close_done(None)

        return self.get_state()

    def refresh(self):
        """Rebuild item cards in place after a state change."""
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
        self._item_list = TreeList(
            self._panel,
            build_forest(self._get_selectable_items(),
                         get_parent=self._get_item_parent,
                         get_children=self._get_item_children,
                         make_key=self._get_item_key),
            self._build_item_card,
            self._is_item_expanded,
            on_toggle=self._on_item_toggle,
            top_down=False,
        )
        self._panel.rows.append(self._item_list)

        # Add button row
        row = SpecterGuiElement(self._panel)
        apply_style(row, "CONTAINER.DROP_UP_ROW")
        self._panel.rows.append(row)

        self._add_button = Btn(
            row,
            icon=BTC_ICONS.PLUS,
            text=self._add_button_label(),
            callback=self._add_cb,
            style="WIDGET.DROP_UP_ADDBTN",
        )
        self._resize_panel()

    def _build_item_card(self, parent, item):
        """Build and size one card for a drop-up item row."""
        card = self._build_card(parent, item)
        if not isinstance(card, InfoCard):
            raise TypeError("DropUp._build_card must return an InfoCard")
        set_size(card, lv.SIZE_CONTENT, lv.SIZE_CONTENT)
        apply_style(card, "LAYOUT.GROWS")
        return card

    def _resize_panel(self):
        """Recalculate the panel's content height and keep its bottom edge fixed."""
        self._panel.update_layout()
        if self._item_list is not None:
            for card in self._item_list.visible_items:
                card.optimize_name_font()
        _, h = get_size(self._panel)
        _, backdrop_h = get_size(self._backdrop)
        set_pos(self._panel, 0, max(backdrop_h - h, 0))

    def _is_item_expanded(self, node):
        key = (self.EXPANSION_CONTEXT, node.key)
        return self.ui_state.is_item_expanded.get(key, False)

    def _on_item_toggle(self, node):
        """Toggle caller-owned state, then refresh and resize the tree."""
        key = (self.EXPANSION_CONTEXT, node.key)
        self.ui_state.is_item_expanded[key] = not self._is_item_expanded(node)
        
        self._item_list.refresh()
        self._resize_panel()

    def _add_cb(self):
        self.close()
        self._navigate_add()

    def _delete_item(self, item):
        """Delete an item and leave the selector when it becomes empty."""
        self._delete_from_gui(item)
        if not self._get_selectable_items():
            self.close()
            self.on_navigate("main")

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

    def _get_selectable_items(self):
        """Return the flat list of items (seeds, wallets, ...) to display."""
        raise NotImplementedError

    def _delete_from_gui(self, item):
        """Remove *item* using the GUI's domain-specific deletion operation."""
        raise NotImplementedError

    def _build_card(self, parent, item):
        """Build and return an ``InfoCard`` inside *parent*."""
        raise NotImplementedError

    def _navigate_add(self):
        """Navigate to the add-item screen."""
        raise NotImplementedError

    def _add_button_label(self):
        """Return text for the add button."""
        raise NotImplementedError

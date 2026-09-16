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
    build_forest, flatten_forest,
    slide_y, delete_all_children_of,
    set_size, set_pos, set_scroll, set_propagate_events,
    get_size, get_pos,
)
from ..symbol_lib import BTC_ICONS
from ..theming import apply_style, remove_style


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
        self._tree_roots = []
        self._expand_all_button = None
        self._collapse_all_button = None
        self._sort_button = None

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
        self._tree_roots = build_forest(
            self._get_selectable_items(),
            get_parent=self._get_item_parent,
            get_children=self._get_item_children,
            make_key=self._get_item_key,
        )
        self._item_list = TreeList(
            self._panel,
            self._tree_roots,
            self._build_item_card,
            self._is_item_expanded,
            on_toggle=self._on_item_toggle,
            top_down=self._is_tree_top_down(),
        )
        self._panel.rows.append(self._item_list)

        # Add button row
        row = SpecterGuiElement(self._panel)
        apply_style(row, "CONTAINER.ADD_BUTTON_ROW")
        self._panel.rows.append(row)

        self._expand_all_button = Btn(
            row,
            icon=BTC_ICONS.TREE_STRUCTURE,
            callback=lambda: self._set_all_item_expanded(True),
            style="WIDGET.ICON_BUTTON",
        )
        self._collapse_all_button = Btn(
            row,
            icon=BTC_ICONS.MENU,
            callback=lambda: self._set_all_item_expanded(False),
            style="WIDGET.ICON_BUTTON",
        )
        self._add_button = Btn(
            row,
            icon=BTC_ICONS.PLUS,
            text=self._add_button_label(),
            callback=self._add_cb,
            style="WIDGET.DROP_UP_ADDBTN",
        )
        self._sort_spacer = Btn(
            row,
            icon=BTC_ICONS.FLIP_VERTICAL,
            style="WIDGET.ICON_BUTTON",
        )
        apply_style(self._sort_spacer, "APPEARANCE.INVISIBLE")
        self._sort_button = Btn(
            row,
            icon=BTC_ICONS.FLIP_VERTICAL,
            callback=self._toggle_tree_direction,
            style="WIDGET.ICON_BUTTON",
        )
        for button in (self._expand_all_button,
                       self._collapse_all_button,
                       self._sort_button,
                       self._sort_spacer):
            apply_style(button, "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)
        self._sort_spacer.set_state(lv.STATE.DISABLED, True)
        self._refresh_tree_controls()
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

    def _is_tree_top_down(self):
        return self.ui_state.is_tree_top_down.get(self.EXPANSION_CONTEXT, False)

    def _set_tree_control_visible(self, button, visible):
        button.set_state(lv.STATE.DISABLED, not visible)

    def _set_tree_control_muted(self, button, muted):
        if muted:
            apply_style(button._ico, "MODIFIER.MUTED")
        else:
            remove_style(button._ico, "MODIFIER.MUTED")

    def _refresh_tree_controls(self):
        """Update fixed control slots from the current forest and view state."""
        branch_nodes = [node for node in flatten_forest(self._tree_roots)
                        if node.has_children()]
        has_hierarchy = bool(branch_nodes)
        if self._expand_all_button is not None:
            self._set_tree_control_visible(self._expand_all_button, has_hierarchy)
            self._set_tree_control_muted(
                self._expand_all_button,
                has_hierarchy and all(self._is_item_expanded(node)
                                      for node in branch_nodes),
            )
        if self._collapse_all_button is not None:
            self._set_tree_control_visible(self._collapse_all_button, has_hierarchy)
            self._set_tree_control_muted(
                self._collapse_all_button,
                has_hierarchy and not any(self._is_item_expanded(node)
                                          for node in branch_nodes),
            )
        if self._sort_button is not None:
            visible_count = (0 if self._item_list is None
                             else len(self._item_list.visible_items))
            self._set_tree_control_visible(self._sort_button, visible_count > 1)

    def _on_item_toggle(self, node):
        """Toggle caller-owned state, then refresh and resize the tree."""
        key = (self.EXPANSION_CONTEXT, node.key)
        self.ui_state.is_item_expanded[key] = not self._is_item_expanded(node)
        
        self._item_list.refresh()
        self._refresh_tree_controls()
        self._resize_panel()

    def _set_all_item_expanded(self, expanded):
        """Expand or collapse every branch in this selector's current forest."""
        for node in flatten_forest(self._tree_roots):
            if node.has_children():
                self.ui_state.is_item_expanded[
                    (self.EXPANSION_CONTEXT, node.key)] = expanded
        if self._item_list is not None:
            self._item_list.refresh()
            self._refresh_tree_controls()
            self._resize_panel()

    def _toggle_tree_direction(self):
        """Reverse this selector's tree direction and redraw its connectors."""
        top_down = not self._is_tree_top_down()
        self.ui_state.is_tree_top_down[self.EXPANSION_CONTEXT] = top_down
        if self._item_list is not None:
            self._item_list.set_top_down(top_down)
            self._refresh_tree_controls()
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

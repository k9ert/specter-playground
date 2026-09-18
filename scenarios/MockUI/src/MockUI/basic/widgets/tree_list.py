"""TreeList -- reusable collapsible hierarchy rows with LVGL line connectors.

Ownership split:
  * The caller builds and owns the ``TreeNode`` forest (items, parent/child
        links) and expanded state, plus the item widgets returned by
    ``build_item(row, item)`` -- including their styles, sizing and callbacks.
  * TreeList owns the row containers, the expander controls, the visible
    ordering and the non-interactive connector layer. It only reads item
    geometry to place connectors.

Theming:
  * ``CONTAINER.TREE_ROW`` is a plain flex-row style (full width; its
    ``pad_column`` provides the gap between gutter controls and items).
  * ``WIDGET.TREE_CONNECTOR`` styles the lines; its ``pad_left`` carries the
    per-depth indent in pixels.
"""

import gc

import lvgl as lv

from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style, get_style_num
from ..symbol_lib import BTC_ICONS
from ..utils import (
    delete_all_children_of,
    make_floating_overlay,
    set_size, get_size, get_pos, set_scroll,
    flatten_forest
)
from .btn import Btn
from .line import Line

class TreeList(SpecterGuiElement):
    """Render a caller-owned ``TreeNode`` forest as collapsible rows.

    ``build_item(row, item)`` must create the row's interactive content and
    return it; all styling and sizing of that content belongs to the caller.
    The created item widgets are exposed (by reference) as ``visible_items``.
    """

    def __init__(self, parent, roots, build_item,
                 is_expanded=None,
                 on_toggle=None,
                 row_style="CONTAINER.TREE_ROW",
                 expander_style="WIDGET.TREE_EXPANDER",
                 connector_style="WIDGET.TREE_CONNECTOR",
                 top_down=True):
        super().__init__(parent)
        apply_style(self, [
            "APPEARANCE.TRANSPARENT",
            "LAYOUT.BARE",
            "LAYOUT.PARENT_WIDTH",
            "LAYOUT.FLEX_COL",
            "LAYOUT.START",
        ])
        set_size(self, height=lv.SIZE_CONTENT)
        set_scroll(self, horizontal=False, vertical=False)

        self._roots = roots
        self._build_item = build_item
        self._is_expanded = is_expanded
        self._row_style = row_style
        self._expander_style = expander_style
        self._connector_style = connector_style
        self._on_toggle = on_toggle
        self._top_down = top_down
        self._has_hierarchy = any(root.children for root in roots)
        if self._has_hierarchy:
            self._expander_width = get_style_num(expander_style, lv.STYLE.WIDTH)
            self._indent = get_style_num(connector_style, lv.STYLE.PAD_LEFT)
            self._leaf_gap = get_style_num(connector_style, lv.STYLE.PAD_RIGHT)
        else:
            self._expander_width = self._indent = 0

        self._rows = []
        self._lines = []
        self.refresh()

    @property
    def visible_items(self):
        """The caller-owned item widgets of the visible rows, in order."""
        return [row.item_widget for row in self._rows]

    def _visible_nodes(self):
        if self._is_expanded is None:
            return flatten_forest(self._roots)

        visible = []
        stack = list(reversed(self._roots))
        while stack:
            node = stack.pop()
            visible.append(node)
            if node.children and self._is_expanded(node):
                stack.extend(reversed(node.children))
        return visible

    def refresh(self):
        """Rebuild rows and connectors from the caller-owned forest."""
        delete_all_children_of(self)
        self._rows = []
        self._lines = []
        gc.collect()

        for node in self._ordered_nodes():
            self._rows.append(self._build_row(node))

        self.update_layout()

        if self._has_hierarchy:
            connector_layer = make_floating_overlay(self)
            width, height = get_size(self)
            set_size(connector_layer, width, height)
            self._draw_connectors(connector_layer)
            connector_layer.move_background()

    def _build_row(self, node):
        """Build and return one full-width row: expander gutter + item.

        The row is a plain styled element; ``node`` and ``item_widget`` are
        attached as plain attributes. Hierarchical rows also have ``expander``
        for the connector and alignment passes.
        """
        row = SpecterGuiElement(self)
        apply_style(row, self._row_style)
        base_padding = row.get_style_pad_left(0)
        row.set_style_pad_left(base_padding + node.depth() * self._indent, 0)
        row.node = node

        if self._has_hierarchy:
            if node.has_children():
                callback = None
                on_toggle = self._on_toggle
                if on_toggle is not None:
                    callback = lambda: on_toggle(node)

                row.expander = Btn(
                    row,
                    icon=self._expander_icon(node),
                    callback=callback,
                    consume_click=True,
                    style=self._expander_style,
                )
            else:
                # Zero-height invisible placeholder sized to the caret's
                # width so leaf items align with parent items.
                row.expander = SpecterGuiElement(row)
                apply_style(row.expander, ["APPEARANCE.INVISIBLE", "LAYOUT.BARE"])
                set_size(row.expander, self._expander_width, 0)

        row.item_widget = self._build_item(row, node.item)
        return row

    def _ordered_nodes(self):
        """Return visible nodes in this list's display direction."""
        nodes = self._visible_nodes()
        return nodes if self._top_down else reversed(nodes)

    def set_top_down(self, top_down):
        """Change display direction and redraw the rows and connectors."""
        if self._top_down == top_down:
            return
        self._top_down = top_down
        self.refresh()

    def _expander_icon(self, node):
        """Return the caret that points toward a parent's visible children."""
        if self._is_expanded is None or self._is_expanded(node):
            return BTC_ICONS.CARET_DOWN if self._top_down else BTC_ICONS.CARET_UP
        return BTC_ICONS.CARET_RIGHT

    def _draw_connectors(self, layer):
        self._lines = [
            Line(layer, x1, y1, x2, y2, self._connector_style)
            for x1, y1, x2, y2 in self._connector_segments()
        ]

    def _connector_segments(self):
        """Return connector endpoints from the current visible row geometry."""
        rows_by_node = {row.node: row for row in self._rows}
        segments = []

        # Vertical stems: from the parent's card edge to its furthest child.
        for row in self._rows:
            node = row.node
            if (not node.children
                    or (self._is_expanded is not None
                        and not self._is_expanded(node))):
                continue
            branch_x = self._expander_center_x(row)
            end_row = rows_by_node[node.children[-1]]
            _, row_y = get_pos(row)
            _, item_y = get_pos(row.item_widget)

            if self._top_down:
                _, item_h = get_size(row.item_widget)
                branch_y = row_y + item_y + item_h
            else:
                branch_y = row_y + item_y

            segments.append(
                (branch_x, branch_y,
                 branch_x, self._card_center_y(end_row)))

        # Horizontal elbows: from the parent's rail to the child's element
        # boundary. The row style's pad_column provides the visible gap.
        for row in self._rows:
            parent = row.node.parent
            if parent is None:
                continue
            parent_row = rows_by_node[parent]

            row_x, _ = get_pos(row)
            right_x = row_x + row.get_style_pad_left(0)
            if not row.node.has_children():
                item_x, _ = get_pos(row.item_widget)
                right_x += item_x
                right_x -= self._leaf_gap

            center_y = self._card_center_y(row)

            segments.append(
                (self._expander_center_x(parent_row), center_y,
                 right_x, center_y))

        return segments

    def _expander_center_x(self, row):
        row_x, _ = get_pos(row)
        return (row_x
                + row.get_style_pad_left(0)
                + self._expander_width // 2)

    @staticmethod
    def _card_center_y(row):
        _, row_y = get_pos(row)
        _, item_y = get_pos(row.item_widget)
        _, item_h = get_size(row.item_widget)
        return row_y + item_y + item_h // 2

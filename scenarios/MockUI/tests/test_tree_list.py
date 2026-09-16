import pytest

from MockUI.basic.utils.tree_node import TreeNode
from MockUI.basic.widgets.tree_list import TreeList
from MockUI.basic.symbol_lib import BTC_ICONS


def _tree(top_down, expanded=True):
    parent = TreeNode("parent")
    child = TreeNode("child")
    parent.add_child(child)

    tree = TreeList.__new__(TreeList)
    tree._roots = [parent]
    tree._is_expanded = lambda node: expanded
    tree._top_down = top_down
    return tree, parent, child


def _nested_tree(expanded, top_down=True):
    root = TreeNode("root")
    child = TreeNode("child")
    grandchild = TreeNode("grandchild")
    second_root = TreeNode("second root")
    root.add_child(child)
    child.add_child(grandchild)

    tree = TreeList.__new__(TreeList)
    tree._roots = [root, second_root]
    tree._is_expanded = lambda node: node.item in expanded
    tree._top_down = top_down
    return tree


def _branching_tree(expanded, top_down):
    root = TreeNode("root")
    collapsed_child = TreeNode("collapsed child")
    hidden_grandchild = TreeNode("hidden grandchild")
    expanded_child = TreeNode("expanded child")
    visible_grandchild = TreeNode("visible grandchild")
    root.add_child(collapsed_child)
    collapsed_child.add_child(hidden_grandchild)
    root.add_child(expanded_child)
    expanded_child.add_child(visible_grandchild)

    tree = TreeList.__new__(TreeList)
    tree._roots = [root]
    tree._is_expanded = lambda node: node.item in expanded
    tree._top_down = top_down
    return tree


class _GeometryObject:
    def __init__(self, x, y, width=0, height=0, left_padding=0):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._left_padding = left_padding
        self.node = TreeNode("placeholder")
        self.item_widget = self

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_style_pad_left(self, part):
        return self._left_padding


@pytest.mark.parametrize(
    "top_down, expected_order",
    [
        (True, ["parent", "child"]),
        (False, ["child", "parent"]),
    ],
)
def test_tree_direction_is_per_instance(top_down, expected_order):
    tree, _, _ = _tree(top_down)

    assert [node.item for node in tree._ordered_nodes()] == expected_order


def test_set_top_down_refreshes_only_when_the_direction_changes():
    tree, _, _ = _tree(top_down=False)
    refreshes = []
    tree.refresh = lambda: refreshes.append(True)

    tree.set_top_down(False)
    tree.set_top_down(True)

    assert tree._top_down is True
    assert refreshes == [True]


@pytest.mark.parametrize(
    "top_down, expanded_icon",
    [
        (True, BTC_ICONS.CARET_DOWN),
        (False, BTC_ICONS.CARET_UP),
    ],
)
def test_expanded_caret_points_toward_children(top_down, expanded_icon):
    tree, parent, _ = _tree(top_down)

    assert tree._expander_icon(parent) == expanded_icon


def test_collapsed_caret_points_to_the_side():
    tree, parent, _ = _tree(top_down=True, expanded=False)

    assert tree._expander_icon(parent) == BTC_ICONS.CARET_RIGHT


@pytest.mark.parametrize(
    "expanded, expected_visible",
    [
        (set(), ["root", "second root"]),
        ({"root"}, ["root", "child", "second root"]),
        ({"root", "child"}, ["root", "child", "grandchild", "second root"]),
    ],
)
def test_visible_nodes_respect_each_ancestor_expansion_state(
        expanded, expected_visible):
    tree = _nested_tree(expanded)

    assert [node.item for node in tree._visible_nodes()] == expected_visible


def test_visible_nodes_without_expansion_state_shows_the_whole_forest():
    tree = _nested_tree(set())
    tree._is_expanded = None

    assert [node.item for node in tree._visible_nodes()] == [
        "root", "child", "grandchild", "second root"]


@pytest.mark.parametrize(
    "top_down, expected_order",
    [
        (True, ["root", "collapsed child", "expanded child",
                "visible grandchild"]),
        (False, ["visible grandchild", "expanded child", "collapsed child",
                 "root"]),
    ],
)
def test_ordered_nodes_keeps_later_expanded_siblings_visible(
        top_down, expected_order):
    tree = _branching_tree(
        {"root", "expanded child"},
        top_down,
    )

    assert [node.item for node in tree._ordered_nodes()] == expected_order


@pytest.mark.parametrize(
    "top_down, expected_icon",
    [
        (True, BTC_ICONS.CARET_DOWN),
        (False, BTC_ICONS.CARET_UP),
    ],
)
def test_no_expansion_callback_shows_parent_as_expanded(top_down, expected_icon):
    tree, parent, _ = _tree(top_down)
    tree._is_expanded = None

    assert tree._expander_icon(parent) == expected_icon


def test_geometry_helpers_use_row_padding_and_item_bounds():
    tree = TreeList.__new__(TreeList)
    tree._expander_width = 21
    row = _GeometryObject(x=40, y=100, left_padding=7)
    row.item_widget = _GeometryObject(x=12, y=3, width=80, height=31)

    assert tree._expander_center_x(row) == 57
    assert tree._card_center_y(row) == 118


@pytest.mark.parametrize(
    "top_down, expected_root_stem_start",
    [
        (True, 30),
        (False, 10),
    ],
)
def test_connector_segments_follow_card_edges_and_leaf_boundaries(
        top_down, expected_root_stem_start):
    root = TreeNode("root")
    nested_child = TreeNode("nested child")
    leaf = TreeNode("leaf")
    root.add_child(nested_child)
    nested_child.add_child(leaf)

    root_row = _GeometryObject(x=0, y=0, left_padding=5)
    root_row.node = root
    root_row.item_widget = _GeometryObject(x=20, y=10, width=100, height=20)
    nested_row = _GeometryObject(x=10, y=50, left_padding=7)
    nested_row.node = nested_child
    nested_row.item_widget = _GeometryObject(x=30, y=5, width=100, height=30)
    leaf_row = _GeometryObject(x=20, y=100, left_padding=9)
    leaf_row.node = leaf
    leaf_row.item_widget = _GeometryObject(x=40, y=4, width=100, height=21)

    tree = TreeList.__new__(TreeList)
    tree._rows = [root_row, nested_row, leaf_row]
    tree._is_expanded = lambda node: True
    tree._top_down = top_down
    tree._expander_width = 20

    expected_segments = [
        (15, expected_root_stem_start, 15, 70),
        (27, 85 if top_down else 55, 27, 114),
        (15, 70, 17, 70),
        (27, 114, 69, 114),
    ]
    assert tree._connector_segments() == expected_segments

    tree._connector_style = None
    tree._draw_connectors(object())

    assert len(tree._lines) == len(expected_segments)


def test_bottom_up_connector_reaches_visually_furthest_direct_child():
    root = TreeNode("root")
    first_child = TreeNode("first child")
    last_child = TreeNode("last child")
    root.add_child(first_child)
    root.add_child(last_child)

    root_row = _GeometryObject(x=0, y=100, left_padding=5)
    root_row.node = root
    root_row.item_widget = _GeometryObject(x=20, y=10, width=100, height=20)
    first_child_row = _GeometryObject(x=10, y=50, left_padding=7)
    first_child_row.node = first_child
    first_child_row.item_widget = _GeometryObject(
        x=30, y=10, width=100, height=20)
    last_child_row = _GeometryObject(x=10, y=0, left_padding=7)
    last_child_row.node = last_child
    last_child_row.item_widget = _GeometryObject(
        x=30, y=10, width=100, height=20)

    tree = TreeList.__new__(TreeList)
    tree._rows = [last_child_row, first_child_row, root_row]
    tree._is_expanded = lambda node: True
    tree._top_down = False
    tree._expander_width = 20

    assert tree._connector_segments()[0] == (15, 110, 15, 20)
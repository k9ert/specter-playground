import pytest
import lvgl as lv

from MockUI.basic.templates.dropup import DropUp, DropUpState
from MockUI.basic.ui_state import Context
from MockUI.basic.widgets.btn import Btn
from MockUI.basic.symbol_lib import BTC_ICONS
from MockUI.basic.symbol_lib.icons.tree_structure import TREE_STRUCTURE
from MockUI.basic.symbol_lib.icons.tree_structure_flipped import TREE_STRUCTURE_FLIPPED
from MockUI.basic.utils.tree_node import TreeNode


class _Panel:
    def __init__(self, calls, width, height):
        self._calls = calls
        self._width = width
        self._height = height
        self.position = None

    def update_layout(self):
        self._calls.append("layout")

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def set_x(self, x):
        self.position = (x, self.position[1] if self.position else None)

    def set_y(self, y):
        self.position = (self.position[0] if self.position else None, y)


class _DeletingPanel:
    def __init__(self):
        self.deleted = False

    def delete(self):
        self.deleted = True


class _Card:
    def __init__(self, calls):
        self._calls = calls

    def optimize_name_font(self):
        self._calls.append("optimize")


class _ItemList:
    def __init__(self, cards):
        self.visible_items = cards


class _RefreshingItemList:
    def __init__(self):
        self.refresh_count = 0
        self.direction_changes = []
        self.visible_items = []

    def refresh(self):
        self.refresh_count += 1

    def set_top_down(self, top_down):
        self.direction_changes.append(top_down)


class _ControlButton:
    def __init__(self):
        self._ico = object()
        self.states = []
        self.disabled_states = []
        self.icons = []

    def set_state(self, state, enabled):
        self.states.append((state, enabled))

    def set_disabled(self, disabled):
        self.disabled_states.append(disabled)

    def update_icon(self, icon):
        self.icons.append(icon)


class _Gui:
    def __init__(self, ui_state):
        self.ui_state = ui_state
        self.refresh_count = 0

    def refresh_ui(self):
        self.refresh_count += 1


class _TestDropUp(DropUp):
    EXPANSION_CONTEXT = Context.SEED

    def __init__(self, items=(), gui=None):
        super().__init__()
        self.items = list(items)
        self._test_gui = gui
        self.deleted_items = []
        self.close_count = 0
        self.navigation_calls = []
        self.add_count = 0
        self.fill_count = 0
        self.resize_count = 0

    def _get_selectable_items(self):
        return self.items

    def _delete_from_gui(self, item):
        self.deleted_items.append(item)
        self.items.remove(item)

    def _navigate_add(self):
        self.add_count += 1

    def _add_button_label(self):
        return "Add"

    def _build_card(self, parent, item):
        raise NotImplementedError

    def _fill_panel(self):
        self.fill_count += 1

    def _resize_panel(self):
        self.resize_count += 1

    def _set_tree_control_visible(self, button, visible):
        button.visible = visible

    def _set_tree_control_muted(self, button, muted):
        button.muted = muted

    def close(self):
        self.close_count += 1

    @property
    def gui(self):
        return self._test_gui

    @property
    def on_navigate(self):
        return self._record_navigation

    def _record_navigation(self, target, **kwargs):
        self.navigation_calls.append((target, kwargs))


class _LifecycleDropUp(DropUp):
    def __init__(self, gui):
        super().__init__()
        self._test_gui = gui

    @property
    def gui(self):
        return self._test_gui


def test_resize_panel_relayouts_after_name_optimization():
    calls = []
    panel = _Panel(calls, width=480, height=120)
    backdrop = _Panel(calls, width=480, height=700)
    card = _Card(calls)

    dropup = DropUp()
    dropup._panel = panel
    dropup._item_list = _ItemList([card])
    dropup._backdrop = backdrop

    dropup._resize_panel()

    assert calls == ["layout", "optimize"]
    assert panel.position == (0, 580)


def test_resize_panel_clamps_to_the_top_when_content_is_taller():
    calls = []
    panel = _Panel(calls, width=480, height=800)
    backdrop = _Panel(calls, width=480, height=700)

    dropup = DropUp()
    dropup._panel = panel
    dropup._item_list = _ItemList([])
    dropup._backdrop = backdrop

    dropup._resize_panel()

    assert calls == ["layout"]
    assert panel.position == (0, 0)


@pytest.mark.parametrize(
    "has_panel, animating, closing, expected_state",
    [
        (False, False, False, DropUpState.CLOSED),
        (True, False, False, DropUpState.OPEN),
        (True, True, False, DropUpState.OPENING),
        (True, True, True, DropUpState.CLOSING),
    ],
)
def test_dropup_state_tracks_panel_and_animation_flags(
        has_panel, animating, closing, expected_state):
    dropup = DropUp()
    dropup._panel = object() if has_panel else None
    dropup._animating = animating
    dropup._closing = closing

    assert dropup.get_state() == expected_state


@pytest.mark.parametrize(
    "animating, closing, expected_refreshes",
    [
        (False, False, 1),
        (True, False, 0),
        (True, True, 0),
    ],
)
def test_refresh_rebuilds_only_an_open_dropup(
        animating, closing, expected_refreshes):
    dropup = _TestDropUp()

    dropup.refresh()
    assert dropup.fill_count == 0

    dropup._panel = object()
    dropup._animating = animating
    dropup._closing = closing
    dropup.refresh()
    assert dropup.fill_count == expected_refreshes


@pytest.mark.parametrize(
    "animating, closing, expected_state",
    [
        (False, False, DropUpState.OPEN),
        (True, False, DropUpState.OPENING),
        (True, True, DropUpState.CLOSING),
    ],
)
def test_open_returns_existing_state_without_rebuilding(
        animating, closing, expected_state):
    dropup = _TestDropUp()
    dropup._panel = object()
    dropup._animating = animating
    dropup._closing = closing

    assert dropup.open(object()) == expected_state
    assert dropup.fill_count == 0


@pytest.mark.parametrize(
    "has_panel, animating, closing, expected_state",
    [
        (False, False, False, DropUpState.CLOSED),
        (True, True, False, DropUpState.OPENING),
        (True, True, True, DropUpState.CLOSING),
    ],
)
def test_close_is_ignored_outside_the_open_state(
        has_panel, animating, closing, expected_state):
    dropup = DropUp()
    dropup._panel = object() if has_panel else None
    dropup._animating = animating
    dropup._closing = closing

    assert dropup.close() == expected_state


def test_close_without_animations_deletes_panel_and_runs_callback(ui_state):
    ui_state.are_animations_enabled = False
    gui = _Gui(ui_state)
    dropup = _LifecycleDropUp(gui)
    panel = _DeletingPanel()
    closed = []
    dropup._panel = panel
    dropup._backdrop = object()
    dropup._on_closed = lambda: closed.append(True)

    assert dropup.close() == DropUpState.CLOSED
    assert panel.deleted is True
    assert dropup._panel is None
    assert dropup._backdrop is None
    assert closed == [True]


def test_cancel_animation_leaves_the_open_panel_ready_for_refresh():
    dropup = DropUp()
    dropup._panel = object()
    dropup._animating = True
    dropup._closing = True
    dropup._anim = object()

    dropup.cancel_animation()

    assert dropup.get_state() == DropUpState.OPEN
    assert dropup._anim is None


def test_toggle_updates_expansion_state_and_refreshes_the_list(ui_state):
    gui = _Gui(ui_state)
    dropup = _TestDropUp(gui=gui)
    dropup._item_list = _RefreshingItemList()
    node = TreeNode("seed", key="fingerprint")

    dropup._on_item_toggle(node)

    assert ui_state.is_item_expanded[(Context.SEED, "fingerprint")] is True
    assert dropup._item_list.refresh_count == 1
    assert dropup.resize_count == 1

    dropup._on_item_toggle(node)

    assert ui_state.is_item_expanded[(Context.SEED, "fingerprint")] is False
    assert dropup._item_list.refresh_count == 2
    assert dropup.resize_count == 2


def test_item_expansion_state_defaults_to_false_and_reads_saved_values(ui_state):
    dropup = _TestDropUp(gui=_Gui(ui_state))
    node = TreeNode("seed", key="fingerprint")
    key = (Context.SEED, "fingerprint")

    assert dropup._is_item_expanded(node) is False

    ui_state.is_item_expanded[key] = True
    assert dropup._is_item_expanded(node) is True

    ui_state.is_item_expanded[key] = False
    assert dropup._is_item_expanded(node) is False


def test_expand_and_collapse_all_updates_every_branch(ui_state):
    gui = _Gui(ui_state)
    dropup = _TestDropUp(gui=gui)
    root = TreeNode("root", key="root")
    child = TreeNode("child", key="child")
    leaf = TreeNode("leaf", key="leaf")
    root.add_child(child)
    child.add_child(leaf)
    dropup._tree_roots = [root]
    dropup._item_list = _RefreshingItemList()

    dropup._set_all_item_expanded(True)

    assert ui_state.is_item_expanded == {
        (Context.SEED, "root"): True,
        (Context.SEED, "child"): True,
    }
    assert dropup._item_list.refresh_count == 1
    assert dropup.resize_count == 1

    dropup._set_all_item_expanded(False)

    assert ui_state.is_item_expanded == {
        (Context.SEED, "root"): False,
        (Context.SEED, "child"): False,
    }
    assert dropup._item_list.refresh_count == 2
    assert dropup.resize_count == 2


def test_tree_controls_keep_slots_and_reflect_available_actions(ui_state):
    dropup = _TestDropUp(gui=_Gui(ui_state))
    root = TreeNode("root", key="root")
    child = TreeNode("child", key="child")
    root.add_child(child)
    dropup._tree_roots = [root]
    dropup._expand_all_button = _ControlButton()
    dropup._collapse_all_button = _ControlButton()
    dropup._sort_button = _ControlButton()
    dropup._item_list = _RefreshingItemList()
    dropup._item_list.visible_items = [root]

    dropup._refresh_tree_controls()

    assert dropup._expand_all_button.visible is True
    assert dropup._expand_all_button.muted is False
    assert dropup._collapse_all_button.visible is True
    assert dropup._collapse_all_button.muted is True
    assert dropup._sort_button.visible is False

    ui_state.is_item_expanded[(Context.SEED, "root")] = True
    dropup._refresh_tree_controls()

    assert dropup._expand_all_button.muted is True
    assert dropup._collapse_all_button.muted is False


def test_tree_control_refresh_updates_available_controls_independently(ui_state):
    dropup = _TestDropUp(gui=_Gui(ui_state))
    root = TreeNode("root", key="root")
    child = TreeNode("child", key="child")
    root.add_child(child)
    dropup._tree_roots = [root]
    dropup._expand_all_button = _ControlButton()

    dropup._refresh_tree_controls()

    assert dropup._expand_all_button.visible is True
    assert dropup._expand_all_button.muted is False


def test_sort_control_appears_when_expansion_shows_multiple_rows(ui_state):
    dropup = _TestDropUp(gui=_Gui(ui_state))
    root = TreeNode("root", key="root")
    child = TreeNode("child", key="child")
    root.add_child(child)
    dropup._tree_roots = [root]
    dropup._expand_all_button = _ControlButton()
    dropup._collapse_all_button = _ControlButton()
    dropup._sort_button = _ControlButton()
    dropup._item_list = _RefreshingItemList()

    dropup._item_list.visible_items = [root]
    dropup._refresh_tree_controls()
    assert dropup._sort_button.visible is False

    dropup._item_list.visible_items = [root, child]
    dropup._refresh_tree_controls()
    assert dropup._sort_button.visible is True


def test_tree_controls_hide_tree_actions_for_a_flat_list(ui_state):
    dropup = _TestDropUp(gui=_Gui(ui_state))
    dropup._tree_roots = [TreeNode("first"), TreeNode("second")]
    dropup._expand_all_button = _ControlButton()
    dropup._collapse_all_button = _ControlButton()
    dropup._sort_button = _ControlButton()
    dropup._item_list = _RefreshingItemList()
    dropup._item_list.visible_items = dropup._tree_roots

    dropup._refresh_tree_controls()

    assert dropup._expand_all_button.visible is False
    assert dropup._collapse_all_button.visible is False
    assert dropup._sort_button.visible is True


def test_hidden_tree_control_uses_the_disabled_state():
    dropup = DropUp()
    button = _ControlButton()

    dropup._set_tree_control_visible(button, False)

    assert button.disabled_states == [True]


def test_btn_set_disabled_updates_wrapper_and_inner_button():
    wrapper = _ControlButton()
    wrapper._btn = _ControlButton()

    Btn.set_disabled(wrapper, True)

    assert wrapper.states == [(lv.STATE.DISABLED, True)]
    assert wrapper._btn.states == [(lv.STATE.DISABLED, True)]


def test_expand_all_icon_tracks_tree_direction(ui_state):
    dropup = _TestDropUp(gui=_Gui(ui_state))
    root = TreeNode("root", key="root")
    root.add_child(TreeNode("child", key="child"))
    dropup._tree_roots = [root]
    dropup._expand_all_button = _ControlButton()

    dropup._refresh_tree_controls()

    assert dropup._expand_all_button.icons[-1] is BTC_ICONS.TREE_STRUCTURE_FLIPPED

    ui_state.is_tree_top_down[Context.SEED] = True
    dropup._refresh_tree_controls()

    assert dropup._expand_all_button.icons[-1] is BTC_ICONS.TREE_STRUCTURE


def test_tree_structure_flipped_icon_reverses_source_rows():
    width = TREE_STRUCTURE.width
    source_rows = [TREE_STRUCTURE.pattern[offset:offset + width]
                   for offset in range(0, len(TREE_STRUCTURE.pattern), width)]

    assert TREE_STRUCTURE_FLIPPED.pattern == b"".join(reversed(source_rows))


def test_tree_direction_defaults_to_bottom_up_and_is_context_specific(ui_state):
    gui = _Gui(ui_state)
    dropup = _TestDropUp(gui=gui)
    dropup._item_list = _RefreshingItemList()

    assert dropup._is_tree_top_down() is False
    assert ui_state.is_tree_top_down.get(Context.WALLET, False) is False

    dropup._toggle_tree_direction()
    dropup._toggle_tree_direction()

    assert ui_state.is_tree_top_down[Context.SEED] is False
    assert ui_state.is_tree_top_down.get(Context.WALLET, False) is False
    assert dropup._item_list.direction_changes == [True, False]
    assert dropup.resize_count == 2


def test_delete_item_closes_and_navigates_only_after_the_last_item():
    dropup = _TestDropUp(items=["first", "last"])

    dropup._delete_item("first")

    assert dropup.deleted_items == ["first"]
    assert dropup.close_count == 0
    assert dropup.navigation_calls == []

    dropup._delete_item("last")

    assert dropup.deleted_items == ["first", "last"]
    assert dropup.close_count == 1
    assert dropup.navigation_calls == [("main", {})]


def test_add_callback_closes_then_navigates_to_add_flow():
    dropup = _TestDropUp()

    dropup._add_cb()

    assert dropup.close_count == 1
    assert dropup.add_count == 1


def test_row_click_reselects_and_refreshes_within_its_active_context(ui_state):
    original_seed = object()
    selected_seed = object()
    ui_state.active_context = Context.SEED
    ui_state.active_seed = original_seed
    gui = _Gui(ui_state)
    dropup = _TestDropUp(gui=gui)

    callback = dropup._make_on_row_click_cb(
        selected_seed,
        Context.SEED,
        "active_seed",
        "set_active_seed",
        "manage_seedphrase",
        "target_seed",
    )
    callback(None)

    assert dropup.close_count == 1
    assert ui_state.active_seed is selected_seed
    assert gui.refresh_count == 1
    assert dropup.navigation_calls == []


@pytest.mark.parametrize(
    "active_context, active_seed",
    [
        (Context.WALLET, object()),
        (Context.SEED, None),
    ],
)
def test_row_click_navigates_when_selection_context_is_unavailable(
        ui_state, active_context, active_seed):
    selected_seed = object()
    ui_state.active_context = active_context
    ui_state.active_seed = active_seed
    gui = _Gui(ui_state)
    dropup = _TestDropUp(gui=gui)

    callback = dropup._make_on_row_click_cb(
        selected_seed,
        Context.SEED,
        "active_seed",
        "set_active_seed",
        "manage_seedphrase",
        "target_seed",
    )
    callback(None)

    assert dropup.close_count == 1
    assert gui.refresh_count == 0
    assert dropup.navigation_calls == [
        ("manage_seedphrase", {"target_seed": selected_seed})]
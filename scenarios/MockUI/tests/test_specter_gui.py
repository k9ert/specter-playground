from types import SimpleNamespace

import MockUI.basic.specter_gui as specter_gui_module
from MockUI.basic.specter_gui import SpecterGui
from MockUI.basic.utils import GUI_REFRESH_MS


def test_periodic_refresh_updates_only_the_battery(monkeypatch):
    callbacks = []
    navigation = []

    class _DeviceState:
        def __init__(self):
            self.battery_cycles = 0

        def debug_cycle_battery(self):
            self.battery_cycles += 1

    class _AppScreen:
        def __init__(self):
            self.battery_refreshes = 0

        def refresh_battery(self):
            self.battery_refreshes += 1

    monkeypatch.setattr(
        specter_gui_module.lv,
        "timer_create",
        lambda callback, period, user_data: callbacks.append(
            (callback, period, user_data)),
    )
    monkeypatch.setattr(specter_gui_module.lv, "screen_load", lambda screen: None)

    gui = SpecterGui.__new__(SpecterGui)
    gui.device_state = _DeviceState()
    gui.app_screen = _AppScreen()
    gui.ui_state = SimpleNamespace(current_menu_id="main")
    gui.navigate_to = lambda menu_id: navigation.append(menu_id)

    SpecterGui.post_init(gui)

    callback, period, user_data = callbacks[0]
    callback(user_data)

    assert navigation == ["main"]
    assert period == GUI_REFRESH_MS
    assert gui.device_state.battery_cycles == 1
    assert gui.app_screen.battery_refreshes == 1
from types import SimpleNamespace

from MockUI.basic.components.navigation_bar import NavigationBar
from MockUI.basic.templates.dropup import DropUpState
from MockUI.basic.ui_state import Context


class _Button:
    def __init__(self):
        self.disabled_states = []
        self.icons = []

    def set_disabled(self, disabled):
        self.disabled_states.append(disabled)

    def set_state(self, *args):
        raise AssertionError("NavigationBar must use Btn.set_disabled()")

    def update_icon(self, icon):
        self.icons.append(icon)


class _DropUp:
    def get_state(self):
        return DropUpState.CLOSED

    def refresh(self):
        raise AssertionError("Closed drop-ups must not be refreshed")


class _NavigationBar(NavigationBar):
    def __init__(self, device_state, current_menu="main", context=Context.MAIN):
        self._device_state = device_state
        self._current_menu = current_menu
        self._context = context
        self._gui = SimpleNamespace(
            device_state=device_state,
            ui_state=SimpleNamespace(_is_animating=False),
        )
        self._seed_dropup = _DropUp()
        self._wallet_dropup = _DropUp()
        self.buttons = {name: _Button()
                        for name in ("Back", "Seed", "Home", "Wallet", "Device")}
        self.states = []

    @property
    def device_state(self):
        return self._device_state

    @property
    def current_menu(self):
        return self._current_menu

    @property
    def context(self):
        return self._context

    @property
    def gui(self):
        return self._gui

    def set_state(self, state, enabled):
        self.states.append((state, enabled))


def test_refresh_uses_public_disabled_api_for_navigation_buttons():
    state = SimpleNamespace(is_locked=False, loaded_seeds=[])
    navigation_bar = _NavigationBar(state)

    navigation_bar.refresh()

    assert navigation_bar.buttons["Back"].disabled_states == [True]
    assert navigation_bar.buttons["Seed"].disabled_states == [True]
    assert navigation_bar.buttons["Home"].disabled_states == [False]
    assert navigation_bar.buttons["Wallet"].disabled_states == [True]
    assert navigation_bar.buttons["Device"].disabled_states == [False]


def test_locked_refresh_disables_every_navigation_button():
    state = SimpleNamespace(is_locked=True, loaded_seeds=[object()])
    navigation_bar = _NavigationBar(state)

    navigation_bar.refresh()

    assert all(button.disabled_states == [True]
               for button in navigation_bar.buttons.values())
import lvgl as lv
from . import GenericMenu, BTN_HEIGHT, BTN_WIDTH
from .symbol_lib import BTC_ICONS
from .widgets import MenuItem


class SwitchAddMenu(GenericMenu):
    """Base class for any menu that let's the user choose an active element from a list and optionally add a new element.
    E.g. switch/add MasterKeys and/or Wallets.

    Should never be used directly, only via subclasses.
    """

    def _build_switch_items(self, elements, label_creation_cb, active_element, activation_cb,
                       add_target_behavior=None, add_string=None, show_check=None):
        """Build a flat item list for *elements*.

        *show_check* - if None, a checkmark is shown only when len(elements) > 1
        (auto-detect).  Pass an explicit bool to override, e.g. when the caller
        assembles a multi-section list via two separate super() calls.
        """
        if show_check is None:
            show_check = len(elements) > 1

        menu_items = []
        for item in elements:
            menu_items.append(MenuItem(
                BTC_ICONS.CHECK if show_check and item is active_element else None,
                label_creation_cb(item),
                self._make_select_cb(activation_cb, item),
            ))

        if add_string and add_target_behavior:
            menu_items.append(MenuItem(BTC_ICONS.PLUS, add_string, add_target_behavior))

        return menu_items

    def _make_select_cb(self, activation_cb, item):
        """Create callback that sets the active item and navigates back."""
        def cb(e):
            if e.get_code() == lv.EVENT.CLICKED:
                activation_cb(item)
                self.gui.refresh_ui()
                self.on_navigate(None)
        return cb
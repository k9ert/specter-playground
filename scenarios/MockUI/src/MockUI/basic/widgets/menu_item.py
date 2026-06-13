"""MenuItem — structured menu item for GenericMenu.get_menu_items().

Usage::
    # Create a coloured section header (e.g. danger zone):
    MenuItem(text=lv.SYMBOL.WARNING + " " + t("DEVICE_MENU_DANGERZONE"), font_color=ORANGE_HEX)
    # Create a regular menu item that navigates to another menu
    MenuItem(BTC_ICONS.MENU, t("WALLET_MENU_VIEW_ADDRESSES"), "view_addresses")
    
    # Create a menu item that triggers a callback function
    MenuItem(BTC_ICONS.TRASH, t("DELETE"), color=RED_HEX, target=cb)

    # Create a menu item with a help popup
    MenuItem(BTC_ICONS.VISIBLE, t("SHOW"), "show_seedphrase",
             color=ORANGE_HEX, help_key="HELP_SHOW_SEED")

    # Create a toggle row (renders with a switch on the right; set_value is called when user toggles)
    MenuItem(BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"),
             get_value=lambda: state.QR_enabled(),
             set_value=state.set_QR_enabled)
"""


class MenuItem:
    """Structured menu item for GenericMenu.

    Args:
        icon:       Icon instance or lv.SYMBOL string, or None (section header).
        text:       Display text.
        target:     None (section header), a menu_id string, or a callable.
        modifier:   semantic modifier: "Danger"/"Warning"/"Highlight".
        height_scaling: Height multiplier float (default 1); minimum 1.
        help_key:   i18n key for a help popup, or None.
        suffix:     List of MenuItemSuffix instances, or None.
        is_submenu: Boolean. Indicates it opens a submenu. (Default False)
        get_value:  Callable → bool.  When set (together with set_value) the
                    item renders as a toggle row.  May also be a plain bool 
                    then it is used as the initial value).
        set_value:  Callable(bool).  Called when the user flips the switch.
    """

    def __init__(self, icon=None, text=None, target=None,
                 modifier=None, height_scaling=None, help_key=None, suffix=None, is_submenu=False,
                 get_value=None, set_value=None):
        if not (modifier in (None, "Danger", "Warning", "Highlight")):
            print(f"MenuItem warning: invalid modifier '{modifier}' for item '{text}', falling back to no modifier")
            modifier = None
        self.icon = icon
        self.text = text
        self.target = target
        self.modifier = modifier
        self.height_scaling = height_scaling
        self.help_key = help_key
        # suffix: list of MenuItemSuffix instances
        # rendered as a right-aligned group of icons/labels inside the button.
        self.suffix = suffix
        self.is_submenu = is_submenu
        self.get_value = get_value
        self.set_value = set_value


class MenuItemSuffix:
    """Structured suffix item for MenuItem.suffix list.

    Args:
        icon:   Icon instance or None (text-only).
        text:   Text to show in suffix, or None (icon-only).
    """
    def __init__(self, icon=None, text=None):
        self.icon = icon
        self.text = text
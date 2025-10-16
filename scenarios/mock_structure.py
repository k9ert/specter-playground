import display
import lvgl as lv
import utime as time

display.init()

BTN_HEIGHT = 60
BTN_WIDTH = 150


class MainMenu(lv.obj):
    def __init__(self, on_navigate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_navigate = on_navigate

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text("What do you want to do?")
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title.align(lv.ALIGN.TOP_MID, 0, 20)

        # Container for buttons
        self.container = lv.obj(self)
        self.container.set_width(lv.pct(100))
        self.container.set_height(lv.pct(80))
        self.container.set_layout(lv.LAYOUT.FLEX)
        self.container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.container.set_style_pad_all(10, 0)
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)

        # Menu items
        menu_items = [
            ("Scan QR", "scan_qr"),
            ("Load File from SD", "load_sd"),
            ("Sign Message", "sign_message"),
            ("Manage Wallet", "manage_wallet"),
            ("Manage Device/Storage", "manage_device"),
            ("Change/Add Wallet", "add_wallet"),
            ("Lock Device", "lock_device"),
        ]

        for text, action in menu_items:
            btn = lv.button(self.container)
            btn.set_width(BTN_WIDTH)
            btn.set_height(BTN_HEIGHT)
            lbl = lv.label(btn)
            lbl.set_text(text)
            lbl.center()
            # Create closure to capture action
            btn.add_event_cb(self.make_callback(action), lv.EVENT.CLICKED, None)

    def make_callback(self, action):
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                self.on_navigate(action)
        return callback


class SubmenuWallet(lv.obj):
    def __init__(self, on_navigate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_navigate = on_navigate

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text("Manage Wallet")
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title.align(lv.ALIGN.TOP_MID, 0, 20)

        # Container for buttons
        self.container = lv.obj(self)
        self.container.set_width(lv.pct(100))
        self.container.set_height(lv.pct(80))
        self.container.set_layout(lv.LAYOUT.FLEX)
        self.container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.container.set_style_pad_all(10, 0)
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)

        # Menu items
        menu_items = [
            ("View Addresses", "view_addresses"),
            ("Manage Seedphrase", "manage_seedphrase"),
            ("Manage Derivation Path", "derivation_path"),
            ("Export Master Public Keys", "export_xpub"),
            ("Rename Wallet", "rename_wallet"),
            ("Delete Wallet", "delete_wallet"),
            ("Back", "main"),
        ]

        for text, action in menu_items:
            btn = lv.button(self.container)
            btn.set_width(BTN_WIDTH)
            btn.set_height(BTN_HEIGHT)
            lbl = lv.label(btn)
            lbl.set_text(text)
            lbl.center()
            btn.add_event_cb(self.make_callback(action), lv.EVENT.CLICKED, None)

    def make_callback(self, action):
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                self.on_navigate(action)
        return callback


class SubmenuDevice(lv.obj):
    def __init__(self, on_navigate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_navigate = on_navigate

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text("Manage Device/Storage")
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title.align(lv.ALIGN.TOP_MID, 0, 20)

        # Container for buttons
        self.container = lv.obj(self)
        self.container.set_width(lv.pct(100))
        self.container.set_height(lv.pct(80))
        self.container.set_layout(lv.LAYOUT.FLEX)
        self.container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.container.set_style_pad_all(10, 0)
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 10)

        # Menu items
        menu_items = [
            ("Manage Backup(s)", "manage_backups"),
            ("Manage Firmware", "manage_firmware"),
            ("Manage Security Features", "manage_security"),
            ("Change Network", "change_network"),
            ("Enable/Disable Interfaces", "interfaces"),
            ("Manage SmartCard", "smartcard"),
            ("Manage SD Card", "sdcard"),
            ("Manage Sounds", "sounds"),
            ("Wipe Device", "wipe_device"),
            ("Back", "main"),
        ]

        for text, action in menu_items:
            btn = lv.button(self.container)
            btn.set_width(BTN_WIDTH)
            btn.set_height(BTN_HEIGHT)
            lbl = lv.label(btn)
            lbl.set_text(text)
            lbl.center()
            btn.add_event_cb(self.make_callback(action), lv.EVENT.CLICKED, None)

    def make_callback(self, action):
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                self.on_navigate(action)
        return callback


class ActionScreen(lv.obj):
    """Generic action screen for menu items"""
    def __init__(self, title, on_navigate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_navigate = on_navigate

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text(title)
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title.align(lv.ALIGN.TOP_MID, 0, 50)

        # Message
        self.msg = lv.label(self)
        self.msg.set_text("Action: " + title)
        self.msg.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.msg.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 30)

        # Back button
        self.back_btn = lv.button(self)
        self.back_btn.set_width(BTN_WIDTH)
        self.back_btn.set_height(BTN_HEIGHT)
        back_lbl = lv.label(self.back_btn)
        back_lbl.set_text("Back")
        back_lbl.center()
        self.back_btn.align_to(self.msg, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.back_btn.add_event_cb(self.on_back, lv.EVENT.CLICKED, None)

    def on_back(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.on_navigate("main")


class NavigationController(lv.obj):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_screen = None
        self.show_menu("main")

    def show_menu(self, menu_name):
        # Delete current screen
        if self.current_screen:
            self.current_screen.delete()

        # Create new screen as child of this controller
        if menu_name == "main":
            self.current_screen = MainMenu(self.show_menu, self)
        elif menu_name == "manage_wallet":
            self.current_screen = SubmenuWallet(self.show_menu, self)
        elif menu_name == "manage_device":
            self.current_screen = SubmenuDevice(self.show_menu, self)
        elif menu_name == "manage_seedphrase":
            self.current_screen = ActionScreen("Manage Seedphrase", self.show_menu, self)
        else:
            # For all other actions, show a generic action screen
            title = menu_name.replace("_", " ")
            title = title[0].upper() + title[1:] if title else ""
            self.current_screen = ActionScreen(title, self.show_menu, self)


scr = NavigationController()


# Needed for LVGL task handling when loaded as main script
def main():
    # Set up the default theme:
    # - disp: pointer to display (None uses the default display)
    # - color_primary: primary color of the theme (blue here)
    # - color_secondary: secondary color of the theme (red here)
    # - dark: True for dark mode, False for light mode (light mode here)
    # - font: font to use (Montserrat 16 here)
    lv.theme_default_init(
        None,
        lv.palette_main(lv.PALETTE.BLUE),
        lv.palette_main(lv.PALETTE.RED),
        False,
        lv.font_montserrat_16,
    )

    lv.screen_load(scr)
    while True:
        time.sleep_ms(30)
        display.update(30)

if __name__ == '__main__':
    main()


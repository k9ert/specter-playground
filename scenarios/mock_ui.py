import display
import lvgl as lv
import utime as time


from MockUI import BTN_HEIGHT, BTN_WIDTH, WalletMenu, DeviceMenu, MainMenu, SpecterState, Wallet, ActionScreen, UIState


display.init()

class NavigationController(lv.obj):
    def __init__(self, specter_state=None, ui_state=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.specter_state = specter_state
        # optional UIState instance used to track menu history
        if ui_state:
            self.ui_state = ui_state
        else:
            self.ui_state = UIState()

        self.current_screen = None

        self.show_menu(self.ui_state.current_menu_id)

    def show_menu(self, target_menu_id=None):
        #if target_menu_id is set, the call was generated traversing "down" the menu hierarchy, and target_menu_id needs to be added to the ui_history
        #if target_menu_id is None this signalizes, the call was generated while traversing "up" the menu hierarchy, i.e. going back, and the ui_history needs to be popped

        # Delete current screen (free memory)
        if self.current_screen:
            self.current_screen.delete()

        # Update UIState navigation history when present
        if target_menu_id is not None:
            # navigating 'down' into target
            self.ui_state.push_menu(target_menu_id)
        else:
            # when moving up/back, pop to previous menu
            self.ui_state.pop_menu()

        # Create new screen (micropython doesn't support match/case)
        current = self.ui_state.current_menu_id
        if current == "main":
            self.current_screen = MainMenu(self.show_menu, self.specter_state, self)
        elif current == "manage_wallet":
            self.current_screen = WalletMenu(self.show_menu, self.specter_state, self)
        elif current == "manage_device":
            self.current_screen = DeviceMenu(self.show_menu, self.specter_state, self)
        elif current == "manage_seedphrase":
            # create ActionScreen and pass origin so Back can return there
            origin = self.ui_state.history[-1] if self.ui_state.history else "main"
            self.current_screen = ActionScreen("Manage Seedphrase", self.show_menu, self)
        else:
            # For all other actions, show a generic action screen
            title = (target_menu_id or "").replace("_", " ")
            title = title[0].upper() + title[1:] if title else ""
            origin = self.ui_state.history[-1] if self.ui_state.history else "main"
            self.current_screen = ActionScreen(title, self.show_menu, self)

singlesig_wallet = Wallet("SingleSigW", xpub="xpub6CUGRUon", isMultiSig=False)

specter_state = SpecterState()
specter_state.has_battery = False
specter_state.hasQR = True
specter_state.enabledQR = True
specter_state.hasSD = False
specter_state.enabledSD = True
specter_state.hasSmartCard = False
specter_state.enabledSmartCard = True
specter_state.pin = "21"
specter_state.language = "eng"
specter_state.registered_wallets.append(singlesig_wallet)
specter_state.set_active_wallet(singlesig_wallet)
specter_state.seed_loaded = True

scr = NavigationController(specter_state)


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


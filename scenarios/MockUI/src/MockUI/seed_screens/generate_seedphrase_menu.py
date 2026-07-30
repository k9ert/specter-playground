
import lvgl as lv
import urandom
from ..basic import (
    SpecterGuiElement,
    TitledScreen, 
    Btn,
    Layout,
    apply_style, 
    make_label, body_label, make_textarea, 
    t,
)
from ..stubs import Seed


class GenerateSeedMenu(TitledScreen):
    """Form to generate a new MasterKey (seedphrase).

    Creates a Seed object; the default wallet is auto-created by
    DeviceState.add_seed().

    menu_id: "generate_seedphrase"
    """

    def __init__(self, parent):
        super().__init__(t("MENU_GENERATE_SEEDPHRASE"), parent)

        apply_style(self.body, ["CONTAINER.MENU_CONTAINER", "LAYOUT.FULL_SIZE", "LAYOUT.FLEX_COL", "LAYOUT.ALL_CENTERED"])
    
        # Key name row
        self.name_row = SpecterGuiElement(self.body)
        apply_style(self.name_row, ["CONTAINER.MENU_ROW"])
        
        name_lbl = make_label(self.name_row, t("COMMON_NAME"))
        apply_style(name_lbl, ["TEXT.TITLE", "FG.DEFAULT"])

        # editable text area — fills remaining width after the label
        self.name_ta = make_textarea(self.name_row)
        apply_style(self.name_ta, ["TEXT.TITLE", "LAYOUT.GROWS"])
        self.name_ta.set_text("Key " + str(urandom.randint(1, 99)))

        keyboard_binder = lambda e: self.gui.keyboard_manager.bind(self.name_ta, Layout.FULL)
        self.name_ta.add_event_cb(keyboard_binder, lv.EVENT.CLICKED, None)

        # Fingerprint preview
        self.generated_fp = Seed._generate_dummy_fingerprint()
        fp_label = make_label(self.body, t("GENERATE_SEED_FINGERPRINT") + self.generated_fp, 
                              ["TEXT.TITLE", "FG.DEFAULT"])

        # Info text
        self.info_label = body_label(self.body, t("GENERATE_SEED_INFO"), "WIDGET.INFO_ITEM")

        # Create button
        self.create_btn = Btn(self.body,
                              text=t("COMMON_CREATE"),
                              callback=self._on_create,
                              background_style="WIDGET.BUTTON",
                              foreground_style="WIDGET.BUTTON_FG"
                              )

    def _on_create(self):
        # read name
        name = self.name_ta.get_text()

        # create seed and auto-create default wallet; set both active
        seed = Seed(label=name, fingerprint=self.generated_fp)
        default_wallet = self.device_state.add_seed(seed)
        self.ui_state.set_active_seed(seed)
        if not self.ui_state.active_wallet:
            self.ui_state.set_active_wallet(default_wallet)

        # Navigate home — navigate_to("main") clears history and runs the exit animation
        self.on_navigate("main")
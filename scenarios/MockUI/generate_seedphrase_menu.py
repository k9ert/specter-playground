import lvgl as lv
import urandom
from .menu import GenericMenu
from .wallet import Wallet
from .ui_consts import SWITCH_HEIGHT, SWITCH_WIDTH, BTN_HEIGHT, BTN_WIDTH


class GenerateSeedMenu(GenericMenu):
    """Menu to generate a new seed and create a wallet.

    menu_id: "generate_seedphrase"
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__("generate_seedphrase", "Generate Seedphrase", [], parent, *args, **kwargs)

        self.parent = parent
        self.state = getattr(parent, "specter_state", None)

        # Wallet name row (bigger than children)
        name_row = lv.obj(self.container)
        name_row.set_width(lv.pct(100))
        name_row.set_height(70)
        name_row.set_layout(lv.LAYOUT.FLEX)
        name_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        name_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        name_row.set_style_border_width(0, 0)

        name_lbl = lv.label(name_row)
        name_lbl.set_text("Wallet name:")
        name_lbl.set_width(lv.pct(30))
        name_lbl.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)

        # editable text area
        self.name_ta = lv.textarea(name_row)
        self.name_ta.set_text("Wallet" + str(urandom.randint(1, 10)) )
        self.name_ta.set_width(lv.pct(60))
        self.name_ta.set_height(40)
  

        # MultiSig row: [SingleSig] [switch] [MultiSig]
        ms_row = lv.obj(self.container)
        ms_row.set_width(lv.pct(100))
        ms_row.set_height(60)
        ms_row.set_layout(lv.LAYOUT.FLEX)
        ms_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        ms_row.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        ms_row.set_style_border_width(0, 0)

        ms_left = lv.label(ms_row)
        ms_left.set_text("SingleSig")
        ms_left.set_width(lv.pct(35))

        self.ms_switch = lv.switch(ms_row)
        self.ms_switch.set_size(SWITCH_HEIGHT, SWITCH_WIDTH)
        # default to single sig
        self.ms_switch.remove_state(lv.STATE.CHECKED)

        ms_right = lv.label(ms_row)
        ms_right.set_text("MultiSig")
        ms_right.set_width(lv.pct(35))

        # Network row: [mainnet] [switch] [testnet]
        net_row = lv.obj(self.container)
        net_row.set_width(lv.pct(100))
        net_row.set_height(60)
        net_row.set_layout(lv.LAYOUT.FLEX)
        net_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        net_row.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        net_row.set_style_border_width(0, 0)

        net_left = lv.label(net_row)
        net_left.set_text("mainnet")
        net_left.set_width(lv.pct(35))

        self.net_switch = lv.switch(net_row)
        self.net_switch.set_size(SWITCH_HEIGHT, SWITCH_WIDTH)
        # default to mainnet
        self.net_switch.remove_state(lv.STATE.CHECKED)

        net_right = lv.label(net_row)
        net_right.set_text("testnet")
        net_right.set_width(lv.pct(35))

        # generate and show xPub above Create
        self.generated_xpub = self._generate_dummy_xpub()
        xp_lbl = lv.label(self.container)
        xp_lbl.set_text("xPub: " + self.generated_xpub)
        xp_lbl.set_width(lv.pct(100))
        xp_lbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

        # Create button row
        create_row = lv.obj(self.container)
        create_row.set_width(lv.pct(100))
        create_row.set_height(80)
        create_row.set_layout(lv.LAYOUT.FLEX)
        create_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        create_row.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        create_row.set_style_border_width(0, 0)

        self.create_btn = lv.button(create_row)
        self.create_btn.set_width(BTN_WIDTH)
        self.create_btn.set_height(BTN_HEIGHT)
        self.create_lbl = lv.label(self.create_btn)
        self.create_lbl.set_text("Create")
        self.create_lbl.center()
        self.create_btn.add_event_cb(lambda e: self._on_create(e), lv.EVENT.CLICKED, None)

    def _generate_dummy_xpub(self):
        try:
            r = urandom.getrandbits(64)
            return "xpub" + hex(r)[2:]
        except Exception:
            import utime

            return "xpub" + hex(int(utime.ticks_ms()))[2:]

    def _on_create(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return

        # read name
        name = self.name_ta.get_text()

        # multisig
        is_ms = bool(self.ms_switch.has_state(lv.STATE.CHECKED))

        # network
        net = "mainnet" if not bool(self.net_switch.has_state(lv.STATE.CHECKED)) else "testnet"

        # create wallet
        w = Wallet(name, self.generated_xpub, is_ms, net)

        # register and set active
        self.state.register_wallet(w)
        self.state.set_active_wallet(w)

        # go to main menu directly
        if hasattr(self.parent, 'ui_state') and self.parent.ui_state:
            self.parent.ui_state.clear_history()
            self.parent.ui_state.current_menu_id = "main"
        self.parent.show_menu(None)


import lvgl as lv
import urandom
from ..basic import (
    BTC_ICONS,
    TitledScreen,
    SpecterGuiElement,
    Btn,
    Layout,
    apply_style,
    set_size,
    make_label,
    make_textarea,
    make_switch,
    Btn,
    t
)
from ..stubs import Wallet

class CreateCustomWalletMenu(TitledScreen):
    """Form to create a custom (dummy) wallet descriptor for testing.

    Allows setting wallet name, singlesig/multisig, network, fingerprints,
    and threshold so the wallet-bar signing indicators can be exercised.

    menu_id: "create_custom_wallet"
    """

    def __init__(self, parent):
        super().__init__(t("ADD_WALLET_CREATE_CUSTOM"), parent)

        apply_style(self.body, ["CONTAINER.MENU_CONTAINER", "LAYOUT.FLEX_COL", "LAYOUT.FULL_SIZE"])


        # ── Wallet name ──────────────────────────────────────────────
        self.body.name_row = SpecterGuiElement(self.body)
        apply_style(self.body.name_row, "CONTAINER.MENU_ROW")
        self.body.name_lbl = make_label(self.body.name_row, t("COMMON_NAME"),
                                        ["FG.DEFAULT", "TEXT.TITLE"])
        self.body.name_ta = make_textarea(self.body.name_row)
        apply_style(self.body.name_ta, ["TEXT.TITLE", "LAYOUT.GROWS"])
        self.body.name_ta.set_text(t("COMMON_WALLET") + " " + str(urandom.randint(1, 99)))
        kb = lambda e: self.keyboard_manager.bind(self.body.name_ta, Layout.FULL)
        self.body.name_ta.add_event_cb(kb, lv.EVENT.CLICKED, None)

        # ── Multisig toggle ──────────────────────────────────────────
        self.body.ms_row = SpecterGuiElement(self.body)
        apply_style(self.body.ms_row, "CONTAINER.MENU_ROW")
        self.body.ms_lbl = make_label(self.body.ms_row, t("COMMON_MULTISIG"), 
                                      ["WIDGET.MENU_LABEL", "TEXT.TITLE"])

        self.body.ms_sw = make_switch(self.body.ms_row, False, setter_cb=lambda e: self._on_multisig_toggle(e))

        # ── Threshold (visible only for multisig) ────────────────────
        self.body.thresh_row = SpecterGuiElement(self.body)
        apply_style(self.body.thresh_row, "CONTAINER.MENU_ROW")
        self.body.thresh_row_lbl = make_label(self.body.thresh_row, t("ADD_WALLET_THRESHOLD"),
                                              ["WIDGET.MENU_LABEL", "TEXT.DEFAULT"])
        self.body.thresh_ta = make_textarea(self.body.thresh_row)
        apply_style(self.body.thresh_ta, ["TEXT.TITLE"])
        self.body.thresh_ta.set_text("2")
        self.body.thresh_ta.set_accepted_chars("0123456789")
        kb2 = lambda e: self.gui.keyboard_manager.bind(self.body.thresh_ta, Layout.FULL)
        self.body.thresh_ta.add_event_cb(kb2, lv.EVENT.CLICKED, None)
        self.body.thresh_row.add_flag(lv.obj.FLAG.HIDDEN)  # hidden until multisig

        # ── Extra fingerprints (for multisig cosigners) ──────────────
        self.body.fp_row = SpecterGuiElement(self.body)
        apply_style(self.body.fp_row, "CONTAINER.MENU_ROW")
        self.body.fp_row_lbl = make_label(self.body.fp_row, t("ADD_WALLET_SIGNERS"),
                                          ["WIDGET.MENU_LABEL", "TEXT.DEFAULT"])
        self.body.fp_ta = make_textarea(self.body.fp_row)
        apply_style(self.body.fp_ta, ["TEXT.DEFAULT", "LAYOUT.GROWS"])
        sig_text = ""
        if self.device_state.loaded_seeds:
            if self.ui_state.active_seed:
                # Pre-fill with active seed's fingerprint for convenience
                fp1 = self.ui_state.active_seed.get_fingerprint()
            else:
                fp1 = self.device_state.loaded_seeds[0].get_fingerprint()

            sig_text = fp1[:]

            if self.device_state.loaded_seeds and len(self.device_state.loaded_seeds) > 1:
                # If multiple seeds are loaded, add a second fingerprint for testing
                fps = [s.get_fingerprint()[:] for s in self.device_state.loaded_seeds if s.get_fingerprint() != fp1]
                sig_text += f",{fps[0][:]}"
            else:
                sig_text += ",0xabcd"
        else:
            sig_text = "0x0123,0xabcd"

        self.body.fp_ta.set_text(sig_text)
        self.body.fp_ta.set_accepted_chars("0123456789abcdefx,")
        kb3 = lambda e: self.gui.keyboard_manager.bind(self.body.fp_ta, Layout.FULL)
        self.body.fp_ta.add_event_cb(kb3, lv.EVENT.CLICKED, None)
        self.body.fp_row.add_flag(lv.obj.FLAG.HIDDEN)

        # ── Network toggle ───────────────────────────────────────────
        self.body.net_row = SpecterGuiElement(self.body)
        apply_style(self.body.net_row, "CONTAINER.MENU_ROW")
        self.body.net_row_lbl = make_label(self.body.net_row, "Testnet", 
                                           ["WIDGET.MENU_LABEL", "TEXT.TITLE"])

        self.body.net_sw = make_switch(self.body.net_row, False, setter_cb=None)

        # ── Custom toggle ───────────────────────────────────────────
        self.body.custom_row = SpecterGuiElement(self.body)
        apply_style(self.body.custom_row, "CONTAINER.MENU_ROW")
        self.body.custom_row_lbl = make_label(self.body.custom_row, t("ADD_WALLET_CUSTOM"),
                                              ["WIDGET.MENU_LABEL", "TEXT.TITLE"])

        self.body.custom_sw = make_switch(self.body.custom_row, False, setter_cb=None)

        # ── Account index ────────────────────────────────────────────
        self.body.acc_row = SpecterGuiElement(self.body)
        apply_style(self.body.acc_row, "CONTAINER.MENU_ROW")
        self.body.acc_row._lbl = make_label(self.body.acc_row, t("WALLET_MENU_SELECT_ACCOUNT"),
                                            ["WIDGET.MENU_LABEL", "TEXT.TITLE"])

        self.account_val = 0
        self.body.acc_row.spin_row = SpecterGuiElement(self.body.acc_row)
        apply_style(self.body.acc_row.spin_row, ["LAYOUT.FLEX_ROW", "LAYOUT.ALL_CENTERED"])
        set_size(self.body.acc_row.spin_row, width=lv.SIZE_CONTENT, height=lv.SIZE_CONTENT)

        self.body.acc_row.spin_row.dec_btn = Btn(self.body.acc_row.spin_row,
                                                  icon=BTC_ICONS.MINUS,
                                                  callback=self._decrement_account,
                                                  background_style="WIDGET.BUTTON",
                                                  foreground_style="WIDGET.BUTTON_FG",
                                                 )
        self.body.acc_row.spin_row.acc_lbl = make_label(self.body.acc_row.spin_row, str(self.account_val),
                                                        ["FG.DEFAULT", "TEXT.TITLE", "TEXT.CENTER"])
        set_size(self.body.acc_row.spin_row.acc_lbl, width=100, height=lv.SIZE_CONTENT)

        self.body.acc_row.spin_row.inc_btn = Btn(self.body.acc_row.spin_row,
                                                 icon=BTC_ICONS.PLUS,
                                                 callback=self._increment_account,
                                                 background_style="WIDGET.BUTTON",
                                                 foreground_style="WIDGET.BUTTON_FG",
                                                )

        # ── Create button ────────────────────────────────────────────
        self.body.btn_row = SpecterGuiElement(self.body)
        apply_style(self.body.btn_row, ["CONTAINER.DROP_UP_ROW"])
        self.create_btn = Btn(
                              self.body.btn_row,
                              text=t("COMMON_CREATE"),
                              callback=self._on_create,
                              background_style="WIDGET.BUTTON",
                              foreground_style="WIDGET.BUTTON_FG"
                             )

    # ── helpers ──────────────────────────────────────────────────────

    def _on_multisig_toggle(self, e):
        if self.body.ms_sw.has_state(lv.STATE.CHECKED):
            self.body.thresh_row.remove_flag(lv.obj.FLAG.HIDDEN)
            self.body.fp_row.remove_flag(lv.obj.FLAG.HIDDEN)
        else:
            self.body.thresh_row.add_flag(lv.obj.FLAG.HIDDEN)
            self.body.fp_row.add_flag(lv.obj.FLAG.HIDDEN)

    def _decrement_account(self):
        if self.account_val > 0:
            self.account_val -= 1
            self.body.acc_row.spin_row.acc_lbl.set_text(str(self.account_val))

    def _increment_account(self):
        if self.account_val < 99:
            self.account_val += 1
            self.body.acc_row.spin_row.acc_lbl.set_text(str(self.account_val))

    def _on_create(self):
        name = self.body.name_ta.get_text()
        is_multi = self.body.ms_sw.has_state(lv.STATE.CHECKED)
        net = "testnet" if self.body.net_sw.has_state(lv.STATE.CHECKED) else "mainnet"
        is_custom = self.body.custom_sw.has_state(lv.STATE.CHECKED)

        # Build fingerprint list
        fps = []
        threshold = int(self.body.thresh_ta.get_text())
        if is_multi:
            # Parse extra cosigner fingerprints
            raw = self.body.fp_ta.get_text().strip()
            if raw:
                for fp in raw.split(","):
                    fp = fp.strip()
                    if fp and fp not in fps:
                        fps.append(fp)
        else:
            # For singlesig, just take the first fingerprint (or 0xabcd if empty)
            raw = self.body.fp_ta.get_text().strip()
            fp = raw.split(",")[0].strip() if raw else "0xabcd"
            fps.append(fp)

        # Build a dummy descriptor string
        if is_custom:
            desc = "fancy script"
        elif is_multi:
            desc = "wsh(sortedmulti(%d,%s))" % (threshold, ",".join(fps))
        else:
            fp0 = fps[0] if fps else "00000000"
            desc = "wpkh([%s/84h/0h/0h]xpub...)" % fp0

        wallet = Wallet(
            label=name,
            descriptor=desc,
            isMultiSig=is_multi,
            net=net,
            required_fingerprints=fps,
            threshold=threshold,
            account=self.account_val,
        )
        self.device_state.register_wallet(wallet)
        self.ui_state.set_active_wallet(wallet)
        self.on_navigate("main")

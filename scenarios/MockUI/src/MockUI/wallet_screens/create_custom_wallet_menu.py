
import lvgl as lv
import urandom
from ..basic import (
    BTC_ICONS,
    TitledScreen, 
    Btn, BTN_HEIGHT, BTN_WIDTH,  
    SCREEN_WIDTH,
    Layout,
    form_label, form_textarea, flex_row,
    style_as_flex_container,
    set_scroll,
    make_switch,
    Btn,
)
from ..stubs import Wallet

class CreateCustomWalletMenu(TitledScreen):
    """Form to create a custom (dummy) wallet descriptor for testing.

    Allows setting wallet name, singlesig/multisig, network, fingerprints,
    and threshold so the wallet-bar signing indicators can be exercised.

    menu_id: "create_custom_wallet"
    """

    def __init__(self, parent):
        super().__init__(parent.i18n.t("ADD_WALLET_CREATE_CUSTOM"), parent)
        t = self.i18n.t

        style_as_flex_container(self.body)

        ROW_H = 60

        # ── Wallet name ──────────────────────────────────────────────
        name_row = self._make_row(ROW_H)
        form_label(name_row, t("COMMON_NAME"), width=lv.pct(25))
        self.name_ta = form_textarea(name_row, width=lv.pct(65))
        self.name_ta.set_text(t("COMMON_WALLET") + " " + str(urandom.randint(1, 99)))
        kb = lambda e: self.gui.keyboard_manager.bind(self.name_ta, Layout.FULL)
        self.name_ta.add_event_cb(kb, lv.EVENT.CLICKED, None)

        # ── Multisig toggle ──────────────────────────────────────────
        ms_row = self._make_row(ROW_H)
        form_label(ms_row, t("COMMON_MULTISIG"), width=lv.pct(50))

        self.ms_sw = make_switch(ms_row, False, setter_cb=lambda e: self._on_multisig_toggle(e))

        # ── Threshold (visible only for multisig) ────────────────────
        self.thresh_row = self._make_row(ROW_H)
        form_label(self.thresh_row, t("ADD_WALLET_THRESHOLD"), width=lv.pct(50))
        self.thresh_ta = form_textarea(self.thresh_row, width=lv.pct(30))
        self.thresh_ta.set_text("2")
        self.thresh_ta.set_accepted_chars("0123456789")
        kb2 = lambda e: self.gui.keyboard_manager.bind(self.thresh_ta, Layout.FULL)
        self.thresh_ta.add_event_cb(kb2, lv.EVENT.CLICKED, None)
        self.thresh_row.add_flag(lv.obj.FLAG.HIDDEN)  # hidden until multisig

        # ── Extra fingerprints (for multisig cosigners) ──────────────
        self.fp_row = self._make_row(ROW_H)
        form_label(self.fp_row, t("ADD_WALLET_SIGNERS"), width=lv.pct(35))

        self.fp_ta = form_textarea(self.fp_row, width=lv.pct(55))
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

        self.fp_ta.set_text(sig_text)
        self.fp_ta.set_accepted_chars("0123456789abcdefx,")
        kb3 = lambda e: self.gui.keyboard_manager.bind(self.fp_ta, Layout.FULL)
        self.fp_ta.add_event_cb(kb3, lv.EVENT.CLICKED, None)
        self.fp_row.add_flag(lv.obj.FLAG.HIDDEN)

        # ── Network toggle ───────────────────────────────────────────
        net_row = self._make_row(ROW_H)
        form_label(net_row, "Testnet", width=lv.pct(50))

        self.net_sw = make_switch(net_row, False, setter_cb=None)

        # ── Custom toggle ───────────────────────────────────────────
        custom_row = self._make_row(ROW_H)
        form_label(custom_row, t("ADD_WALLET_CUSTOM"), width=lv.pct(50))

        self.custom_sw = make_switch(custom_row, False, setter_cb=None)

        # ── Account index ────────────────────────────────────────────
        acc_row = self._make_row(ROW_H)
        form_label(acc_row, t("WALLET_MENU_SELECT_ACCOUNT"), width=lv.pct(50))

        self.account_val = 0
        spin_row = flex_row(acc_row, height=ROW_H - 4, width = lv.SIZE_CONTENT)

        def _dec_cb(e):
            if e.get_code() == lv.EVENT.CLICKED and self.account_val > 0:
                self.account_val -= 1
                self.acc_lbl.set_text(str(self.account_val))

        def _inc_cb(e):
            if e.get_code() == lv.EVENT.CLICKED and self.account_val < 99:
                self.account_val += 1
                self.acc_lbl.set_text(str(self.account_val))

        btn_sz = ROW_H - 14
        dec_btn = Btn(spin_row,
                      icon=BTC_ICONS.MINUS,
                      size=(btn_sz, btn_sz),
                      callback=_dec_cb
                    )
        self.acc_lbl = form_label(spin_row, str(self.account_val), width=50)
        self.acc_lbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

        inc_btn = Btn(spin_row,
                      icon=BTC_ICONS.PLUS,
                      size=(btn_sz, btn_sz),
                      callback=_inc_cb
                    )

        # ── Create button ────────────────────────────────────────────
        btn_row = self._make_row(80)
        self.create_btn = Btn(
            btn_row,
            text=t("COMMON_CREATE"),
            size=(BTN_WIDTH, BTN_HEIGHT),
            callback=lambda e: self._on_create(e),
        )

    # ── helpers ──────────────────────────────────────────────────────

    def _make_row(self, height):
        row = flex_row(self.body, height=height, width=SCREEN_WIDTH, main_align=lv.FLEX_ALIGN.SPACE_BETWEEN)
        set_scroll(row, horizontal=False, vertical=False)
        return row

    def _on_multisig_toggle(self, e):
        if self.ms_sw.has_state(lv.STATE.CHECKED):
            self.thresh_row.remove_flag(lv.obj.FLAG.HIDDEN)
            self.fp_row.remove_flag(lv.obj.FLAG.HIDDEN)
        else:
            self.thresh_row.add_flag(lv.obj.FLAG.HIDDEN)
            self.fp_row.add_flag(lv.obj.FLAG.HIDDEN)

    def _on_create(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return

        name = self.name_ta.get_text()
        is_multi = self.ms_sw.has_state(lv.STATE.CHECKED)
        net = "testnet" if self.net_sw.has_state(lv.STATE.CHECKED) else "mainnet"
        is_custom = self.custom_sw.has_state(lv.STATE.CHECKED)

        # Build fingerprint list
        fps = []
        threshold = int(self.thresh_ta.get_text())
        if is_multi:
            # Parse extra cosigner fingerprints
            raw = self.fp_ta.get_text().strip()
            if raw:
                for fp in raw.split(","):
                    fp = fp.strip()
                    if fp and fp not in fps:
                        fps.append(fp)
        else:
            # For singlesig, just take the first fingerprint (or 0xabcd if empty)
            raw = self.fp_ta.get_text().strip()
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

import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH, MODAL_HEIGHT_PCT, MODAL_WIDTH_PCT, SWITCH_HEIGHT, SWITCH_WIDTH, PAD, SMALL_PAD, SMALL_TEXT_FONT, BTC_ICON_WIDTH, DEFAULT_MODAL_BG_OPA, SCREEN_WIDTH, SCREEN_HEIGHT
from .titled_screen import TitledScreen
from .symbol_lib import Icon, BTC_ICONS
from .widgets.modal_overlay import ModalOverlay
from .widgets.btn import Btn
from .widgets.containers import flex_col, dialog_card, flex_row
from .widgets.labels import body_label, section_header, form_label
from .widgets.icon_widgets import make_icon
from .specter_gui_base import delete_all_children_of



class GenericMenu(TitledScreen):
    """Reusable menu builder — template method pattern.

    Subclasses override the three hooks:
        get_title(t, state)      -> str          title shown at the top
        get_menu_items(t, state) -> list         list of MenuItems; will be used to create the actual menu
        post_init(t, state)      -> None         called after all LVGL widgets are built (optional)
    """

    def __init__(self, parent):
        # TitledScreen sets self.gui, self.device_state, self.ui_state, self.i18n, self.on_navigate, self.body, etc.
        super().__init__("", parent)

        if self.title:
            title = self.get_title(self.t, self.device_state)
            self.title.set_text(title)

        self.body.set_layout(lv.LAYOUT.FLEX)
        self.body.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.body.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.fill_body()

    def refresh(self):
        # Delegate to TitledScreen (updates battery, context bar, etc.)
        super().refresh()

    def fill_body(self):
        menu_items = self.get_menu_items(self.t, self.device_state)
        self._build_menu_items(menu_items)
        self.post_init(self.t, self.device_state)
        self._configure_scroll()

    def rebuild_body(self):
        delete_all_children_of(self.body)
        self.fill_body()

    def _build_menu_items(self, menu_items):
        """Build LVGL widgets for each item in the menu_items list."""
        for item in menu_items:
            icon = item.icon
            text = item.text
            target_behavior = item.target
            color = item.color
            fontcolor = item.font_color
            size = item.size
            help_key = item.help_key
            get_value = item.get_value
            set_value = item.set_value
            is_submenu = item.is_submenu

            # Normalize size: default to 1, ensure minimum of 1
            if size is None or size < 1:
                size = 1

            if target_behavior is None and (get_value is None or set_value is None):
                section_header(self.body, text, color=fontcolor)
            elif get_value is not None and set_value is not None:
                # ── Toggle row ─────────────────────────────────────────────
                row = flex_row(self.body, height=SWITCH_HEIGHT, main_align=lv.FLEX_ALIGN.START)
                row.set_style_pad_column(PAD, 0)
                if icon and isinstance(icon, Icon):
                    make_icon(row, icon)
                elif icon:
                    ico = body_label(row, icon, recolor=True, width=lv.SIZE_CONTENT)
                lbl = form_label(row, text, width=None)
                lbl.set_flex_grow(1)
                if help_key:
                    self._add_help_btn(row, (SWITCH_HEIGHT, SWITCH_HEIGHT), text, help_key, fontcolor)
                sw = lv.switch(row)
                sw.set_size(SWITCH_HEIGHT, SWITCH_WIDTH)
                
                #set init state
                current = get_value() if callable(get_value) else get_value
                if current:
                    sw.add_state(lv.STATE.CHECKED)
                else:
                    sw.remove_state(lv.STATE.CHECKED)

                def _make_toggle_cb(setter):
                    def _cb(e):
                        is_on = bool(e.get_target_obj().has_state(lv.STATE.CHECKED))
                        setter(is_on)
                        self.gui.refresh_ui()
                    return _cb
                sw.add_event_cb(_make_toggle_cb(item.set_value), lv.EVENT.VALUE_CHANGED, None)
            else:
                # Btn: icon is positioned manually at LEFT_MID so it
                # stays left-aligned regardless of text length (not using flex).
                btn = Btn(
                    self.body,
                    text=text,
                    color=color if color else None,
                    fontcolor=fontcolor,
                    size=(lv.pct(BTN_WIDTH), int(BTN_HEIGHT * size)),
                )
                # Icon instance (BTC_ICONS.*) — add as image at left edge
                if icon and isinstance(icon, Icon):
                    make_icon(btn._btn, icon, color=fontcolor).align(lv.ALIGN.LEFT_MID, PAD, 0)
                # String symbols (lv.SYMBOL.*) — add as recolor label at left edge
                elif icon:
                    body_label(btn._btn, icon, width=lv.SIZE_CONTENT, color=fontcolor, recolor=True).align(lv.ALIGN.LEFT_MID, PAD, 0)

                # Right-side container: [suffixes...] [help?] [caret — always reserved]
                right_cont = flex_row(btn._btn, width=lv.SIZE_CONTENT, height=lv.pct(100), main_align=lv.FLEX_ALIGN.START)
                right_cont.set_style_bg_opa(lv.OPA.TRANSP, 0)
                right_cont.set_style_pad_column(SMALL_PAD, 0)
                right_cont.remove_flag(lv.obj.FLAG.CLICKABLE)
                right_cont.set_scroll_dir(lv.DIR.NONE)
                right_cont.add_flag(lv.obj.FLAG.FLOATING)

                for suf in (item.suffix or []):
                    if suf.icon is not None:
                        make_icon(right_cont, suf.icon, suf.color)
                    if suf.text is not None:
                        body_label(right_cont, suf.text, width=lv.SIZE_CONTENT, font=SMALL_TEXT_FONT, color=suf.color)

                if help_key:
                    self._add_help_btn(right_cont, (BTC_ICON_WIDTH, BTC_ICON_WIDTH), text, help_key, fontcolor)

                if is_submenu:
                    make_icon(right_cont, BTC_ICONS.CARET_RIGHT, fontcolor)

                right_cont.update_layout()
                right_cont.align(lv.ALIGN.RIGHT_MID, -SMALL_PAD, 0)

                btn.add_event_cb(self.make_menu_button_callback(target_behavior), lv.EVENT.CLICKED, None)

    # --- template-method hooks -------------------------------------------

    TITLE_KEY = None  # set in subclass to avoid overriding get_title

    def get_title(self, t, state):
        """Return the menu title string. Override in subclasses, or just set TITLE_KEY."""
        return t(self.TITLE_KEY) if self.TITLE_KEY else ""

    def get_menu_items(self, t, state):
        """Return the list of MenuItems."""
        return []

    def post_init(self, t, state):
        """Called after all LVGL widgets are built. Override for post-construction work."""
        pass

    # --- internal helpers -------------------------------------------------

    def make_menu_button_callback(self, target_behavior):
        """Create callback for button - handles both string menu_ids and custom callables."""
        # If it's already a callable, return it directly
        if callable(target_behavior):
            return target_behavior
        
        # Otherwise, it's a string menu_id - create navigation callback
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                if not self.on_navigate:
                    return
                self.on_navigate(target_behavior)
        return callback

    def _add_help_btn(self, parent, size, text, help_key, fontcolor):
        """Add a transparent help icon button to *parent*."""
        btn = Btn(parent, icon=BTC_ICONS.QUESTION_CIRCLE, fontcolor=fontcolor, size=size)
        btn.make_background_transparent()
        btn.add_event_cb(self.make_help_callback(text, help_key), lv.EVENT.CLICKED, None)

    def make_help_callback(self, title_text, help_key):
        """Create callback for help button - shows a modal overlay with help text."""
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                help_text = self.t(help_key)

                modal = ModalOverlay(bg_opa=DEFAULT_MODAL_BG_OPA)
                # --- dialog card ---
                dw = SCREEN_WIDTH * MODAL_WIDTH_PCT // 100
                dh = SCREEN_HEIGHT * MODAL_HEIGHT_PCT // 100
                dx = (SCREEN_WIDTH - dw) // 2
                dy = (SCREEN_HEIGHT - dh) // 2
                dialog = dialog_card(modal.overlay, dw, dh, dx, dy)

                body_label(dialog, title_text)
                body_label(dialog, help_text)

                close_btn = Btn(
                    dialog,
                    text=self.t("MODAL_CLOSE_BTN"),
                    callback=lambda ev: modal.close() if ev.get_code() == lv.EVENT.CLICKED else None,
                )

                # stop the underlying button from firing too
                e.stop_bubbling = 1
        return callback

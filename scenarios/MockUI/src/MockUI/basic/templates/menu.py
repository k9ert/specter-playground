import lvgl as lv
from ..utils.ui_consts import BTN_HEIGHT, BTN_WIDTH, MODAL_HEIGHT_PCT, MODAL_WIDTH_PCT, SWITCH_HEIGHT, SWITCH_WIDTH, PAD, SMALL_PAD, SMALL_TEXT_FONT, BTC_ICON_WIDTH, DEFAULT_MODAL_BG_OPA, SCREEN_WIDTH, SCREEN_HEIGHT
from .titled_screen import TitledScreen
from ..symbol_lib import Icon, BTC_ICONS
from ..widgets.modal_overlay import ModalOverlay
from ..widgets.action_modal import ActionModal
from ..widgets.btn import Btn
from ..widgets.containers import flex_col, dialog_card, flex_row
from ..widgets.labels import body_label, section_header, form_label
from ..widgets.icon_widgets import make_icon
from ..utils.ui_utils import configure_flex, delete_all_children_of


class GenericMenu(TitledScreen):
    """Reusable menu builder — template method pattern.

    Subclasses override the three hooks:
        get_title(t, state)      -> str          title shown at the top
        get_menu_items(t, state) -> list         list of MenuItems; will be used to create the actual menu
        pre_init(t, state)       -> None         called before menu items are built (optional)
        post_init(t, state)      -> None         called after all LVGL widgets are built (optional)
    """

    def __init__(self, parent):
        # TitledScreen sets self.gui, self.device_state, self.ui_state, self.i18n, self.on_navigate, self.body, etc.
        super().__init__("", parent)

        if self.title:
            title = self.get_title(self.t, self.device_state)
            self.title.set_text(title)

        self.body.set_layout(lv.LAYOUT.FLEX)
        configure_flex(self.body)
        self.fill_body()

    def refresh(self):
        # Delegate to TitledScreen (updates battery, context bar, etc.)
        super().refresh()

    def fill_body(self):
        menu_items = self.get_menu_items(self.t, self.device_state)
        self.pre_init(self.t, self.device_state)
        self._build_menu_items(menu_items)
        self.post_init(self.t, self.device_state)
        self._configure_scroll()

    def rebuild_body(self):
        delete_all_children_of(self.body)
        self.fill_body()

    def _build_menu_items(self, menu_items):
        """Dispatch each MenuItem to the appropriate row builder."""
        for item in menu_items:
            if item.target is None and (item.get_value is None or item.set_value is None):
                self._build_section_row(item)
            elif item.get_value is not None and item.set_value is not None:
                self._build_toggle_row(item)
            else:
                self._build_button_row(item)

    def _build_section_row(self, item):
        """Section header row: optional icon + bold/coloured heading label."""
        row = flex_row(self.body, width=lv.pct(100), main_align=lv.FLEX_ALIGN.START)
        if item.icon and isinstance(item.icon, Icon):
            make_icon(row, item.icon, color=item.font_color if item.font_color else None)
        section_header(row, item.text, color=item.font_color).set_flex_grow(1)

    def _build_toggle_row(self, item):
        """Switch row: icon + label + optional help + lv.switch wired to get/set_value."""
        row = flex_row(self.body, height=SWITCH_HEIGHT, main_align=lv.FLEX_ALIGN.START)
        row.set_style_pad_column(PAD, 0)
        if item.icon and isinstance(item.icon, Icon):
            make_icon(row, item.icon)
        elif item.icon:
            body_label(row, item.icon, recolor=True, width=lv.SIZE_CONTENT)
        lbl = form_label(row, item.text, width=None)
        lbl.set_flex_grow(1)
        if item.help_key:
            self._add_help_btn(row, (SWITCH_HEIGHT, SWITCH_HEIGHT), item.text, item.help_key, item.font_color)
        sw = lv.switch(row)
        sw.set_size(SWITCH_HEIGHT, SWITCH_WIDTH)

        # Set initial state
        current = item.get_value() if callable(item.get_value) else item.get_value
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

    def _build_button_row(self, item):
        """Full menu button: icon + text + right-side suffixes/help/caret."""
        # Normalize size: default to 1, ensure minimum of 1
        size = item.size if item.size and item.size >= 1 else 1

        # Btn: icon is positioned manually at LEFT_MID so it stays left-aligned
        # regardless of text length (not using flex).
        btn = Btn(
            self.body,
            text=item.text,
            color=item.color if item.color else None,
            fontcolor=item.font_color,
            size=(lv.pct(BTN_WIDTH), int(BTN_HEIGHT * size)),
        )
        # Icon instance (BTC_ICONS.*) — add as image at left edge
        if item.icon and isinstance(item.icon, Icon):
            make_icon(btn._btn, item.icon, color=item.font_color).align(lv.ALIGN.LEFT_MID, PAD, 0)
        # String symbols (lv.SYMBOL.*) — add as recolor label at left edge
        elif item.icon:
            body_label(btn._btn, item.icon, width=lv.SIZE_CONTENT, color=item.font_color, recolor=True).align(lv.ALIGN.LEFT_MID, PAD, 0)

        # Right-side container: [suffixes...] [help?] [caret — always reserved]
        right_cont = flex_row(
            btn._btn,
            width=lv.SIZE_CONTENT,
            height=lv.pct(100),
            main_align=lv.FLEX_ALIGN.START,
            transparent_bg=True,
        )
        right_cont.set_style_pad_column(SMALL_PAD, 0)
        right_cont.remove_flag(lv.obj.FLAG.CLICKABLE)
        right_cont.set_scroll_dir(lv.DIR.NONE)
        right_cont.add_flag(lv.obj.FLAG.FLOATING)

        for suf in (item.suffix or []):
            if suf.icon is not None:
                make_icon(right_cont, suf.icon, suf.color)
            if suf.text is not None:
                body_label(right_cont, suf.text, width=lv.SIZE_CONTENT, font=SMALL_TEXT_FONT, color=suf.color)

        if item.help_key:
            self._add_help_btn(right_cont, (BTC_ICON_WIDTH, BTC_ICON_WIDTH), item.text, item.help_key, item.font_color)

        if item.is_submenu:
            make_icon(right_cont, BTC_ICONS.CARET_RIGHT, item.font_color)

        right_cont.update_layout()
        right_cont.align(lv.ALIGN.RIGHT_MID, -SMALL_PAD, 0)

        btn.add_event_cb(self.make_menu_button_callback(item.target), lv.EVENT.CLICKED, None)

    # --- template-method hooks -------------------------------------------

    TITLE_KEY = None  # set in subclass to avoid overriding get_title

    def get_title(self, t, state):
        """Return the menu title string. Override in subclasses, or just set TITLE_KEY."""
        return t(self.TITLE_KEY) if self.TITLE_KEY else ""

    def get_menu_items(self, t, state):
        """Return the list of MenuItems."""
        return []

    def pre_init(self, t, state):
        """Called before menu items are built. Override to insert widgets above the item list."""
        pass

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
        btn = Btn(parent, icon=BTC_ICONS.QUESTION_CIRCLE, fontcolor=fontcolor, size=size, transparent=True,)
        btn.add_event_cb(self.make_help_callback(text, help_key), lv.EVENT.CLICKED, None)

    def make_help_callback(self, title_text, help_key):
        """Create callback for help button - shows a modal overlay with help text."""
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                ActionModal(text=title_text + "\n" + self.t(help_key))
                # stop the underlying button from firing too
                e.stop_bubbling = 1
        return callback

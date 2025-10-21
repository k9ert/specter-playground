import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH, MENU_PCT


class GenericMenu(lv.obj):
    """Reusable menu builder.

    title: string title shown at top
    menu_items: list of (text, action) where action=None creates a label/spacer
    """

    def __init__(self, menu_id, title, menu_items, parent, *args, **kwargs):
        # parent is the NavigationController (not necessarily the LVGL parent)
        # attach to parent's `content` container when available so the status bar stays visible
        lv_parent = getattr(parent, "content", parent)
        super().__init__(lv_parent, *args, **kwargs)
        # discover navigation callback and shared state from parent
        self.on_navigate = getattr(parent, "on_navigate", None)
        # optional shared state object (SpecterState) is stored on parent
        self.state = getattr(parent, "specter_state", None)
        # identifier for this menu (used e.g. as a return target)
        self.menu_id = menu_id

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text(title)
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        # reduce vertical space used by the title
        self.title.align(lv.ALIGN.TOP_MID, 0, 6)

        # Container for buttons
        self.container = lv.obj(self)
        self.container.set_width(lv.pct(100))
        self.container.set_height(lv.pct(MENU_PCT))
        self.container.set_layout(lv.LAYOUT.FLEX)
        self.container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.container.set_style_pad_all(6, 0)
        # smaller gap between title and container
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 6)

        # Build items
        for text, target_menu_id in menu_items:
            if target_menu_id is None:
                spacer = lv.label(self.container)
                spacer.set_text(text or "")
                spacer.set_width(BTN_WIDTH)
                spacer.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
            else:
                btn = lv.button(self.container)
                btn.set_width(BTN_WIDTH)
                btn.set_height(BTN_HEIGHT)
                lbl = lv.label(btn)
                lbl.set_text(text)
                lbl.center()
                btn.add_event_cb(self.make_callback(target_menu_id), lv.EVENT.CLICKED, None)

    def make_callback(self, target_menu_id):
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                if not self.on_navigate:
                    return
                if target_menu_id == "back":
                    self.on_navigate(None)
                else:
                    self.on_navigate(target_menu_id)
        return callback

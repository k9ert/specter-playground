import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH
from .titled_screen import TitledScreen
from .widgets.btn import Btn
from .widgets.labels import body_label

class ActionScreen(TitledScreen):
    """Generic action screen for menu items.
    
    Displays a message and a back button. The message is based on the title but can be extended with a prefix/suffix if needed.

    Used in MockUI as a placeholder for menus/screens that haven't been implemented yet.
    Should not be used in production code.
    """
    def __init__(self, title, parent):

        #Make title look nicer
        title = title.replace("_", " ") if title else ""
        title = title[0].upper() + title[1:] if title else ""

        # TitledScreen creates title_bar and body
        super().__init__(title, parent)

        # Message – placed inside body
        self.msg = body_label(self.body, self.t("ACTION_SCREEN_PREFIX") + title)
        self.msg.align(lv.ALIGN.TOP_MID, 0, 20)

        # Back button – placed inside body below the message
        self.action_back_btn = Btn(
            self.body,
            text=self.t("ACTION_SCREEN_BACK"),
            size=(lv.pct(BTN_WIDTH), BTN_HEIGHT),
            callback=self.on_back,
        )
        self.action_back_btn.align_to(self.msg, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)

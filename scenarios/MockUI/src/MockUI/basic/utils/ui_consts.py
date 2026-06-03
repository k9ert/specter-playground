from micropython import const
import lvgl as lv


SCREEN_WIDTH = const(480)
SCREEN_HEIGHT = const(800)

# --- Menu / button sizes ---
BTN_HEIGHT = const(75)           # menu button height (px)
BTN_WIDTH = const(100)           # menu button width (percent of screen width)
PIN_BTN_HEIGHT = const(85)       # lock screen PIN keypad button height (px)
PIN_BTN_WIDTH = const(115)       # lock screen PIN keypad button width (px)
BACK_BTN_HEIGHT = const(70)      # back button height (px)
BACK_BTN_WIDTH = const(48)       # back button width (px)
MENU_PCT = const(100)
TITLE_ROW_HEIGHT = const(60)     # fixed height reserved for the title + back-btn row
TITLE_TA_WIDTH = const(200)      # width of editable title text area (px)
TITLE_PADDING = const(15)        # gap between title row and button container
STATUS_BTN_HEIGHT = const(50)    # status bar button height (was 30)
STATUS_BTN_WIDTH = const(60)     # status bar button width  (was 40)
SWITCH_HEIGHT = const(82)        # toggle switch height (was 55)
SWITCH_WIDTH = const(45)         # toggle switch width  (was 30)
FINGERPRINT_LBL_WIDTH = const(40)  # width of fingerprint labels (px)

SMALL_PAD = const(4)
PAD = const(8)
BIG_PAD = const(12)

CARD_H = STATUS_BTN_HEIGHT + 2 * BIG_PAD + 2  # context-bar card height (shared by dropup, seed, wallet)

# --- Status bar / content area layout ---
STATUS_BAR_PCT = const(8)        # navigation bar (bottom), % of screen height
CONTENT_PCT = const(92)          # 100 - STATUS_BAR_PCT (no top bar)
BATTERY_WIDTH = const(50)        # battery widget width (px)

# --- Navigation history ---
MAX_HISTORY_DEPTH = const(10)      # maximum number of entries in the back-navigation stack

# --- Icon sizes ---
BTC_ICON_WIDTH = const(42)            # layout space per icon (native bitmap size)
BTC_ICON_ZOOM = const(256)            # LVGL zoom: 256=100% — bitmap is already 42×42, no scaling needed

# --- Font sizes (FontLoaderDE, sizes 8–28 available) ---
MENU_TITLE_FONT_SIZE = const(24)  # screen/menu title font
MENU_ITEM_FONT_SIZE = const(20)   # menu item labels and status bar labels

# Modal/popup 
MODAL_WIDTH_PCT = const(75)  # width of modals as percentage of screen width
MODAL_HEIGHT_PCT = const(75) # height of modals as percentage of screen height
DIALOG_RADIUS = const(8)     # corner radius for dialog cards
DEFAULT_MODAL_BG_OPA = const(180)  # default backdrop opacity for modals (0-255, ~70% = 180)

# Confirmation slider
CONFIRMATION_SLIDER_HEIGHT = BTN_HEIGHT  # slider height matches button height

# DropUp style
DROPUP_DIVIDER_OPA = const(200)  # opacity of divider line between dropup items (0-255, ~80% = 200)

# UIExplainer dimensions and style
EXPLAINER_WIDTH_PCT = const(70)   # Width of explainer text box (percentage of screen)
EXPLAINER_HEIGHT_PCT = const(40)  # Height of explainer text box (percentage of screen)

# Animation constants
ANIM_MS_HORIZONTAL = const(150)   # horizontal slide duration (ms)
ANIM_MS_VERTICAL = const(300)     # vertical slide duration (ms)
GUI_REFRESH_MS = const(2000)      # periodic UI refresh interval (ms)

# Fonts
TITLE_FONT = lv.font_montserrat_28
TEXT_FONT = lv.font_montserrat_22
SMALL_TEXT_FONT = lv.font_montserrat_16

GREEN = const("#00D100")
GREEN_HEX = lv.color_hex(0x00D100)
ORANGE = const("#FF9A00")
ORANGE_HEX = lv.color_hex(0xFF9A00)
RED = const("#F10000")
RED_HEX = lv.color_hex(0xF10000)
WHITE = const("#FFFFFF")
WHITE_HEX = lv.color_hex(0xFFFFFF)
GREY = const("#606060")
GREY_HEX = lv.color_hex(0x606060)
BLACK = const("#000000")
BLACK_HEX = lv.color_hex(0x000000)

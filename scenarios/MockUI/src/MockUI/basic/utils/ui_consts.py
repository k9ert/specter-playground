from micropython import const
import lvgl as lv


SCREEN_WIDTH = const(480)
SCREEN_HEIGHT = const(800)

# --- Menu / button sizes ---
BTN_HEIGHT = const(75)           # menu button height (px)
BTN_WIDTH_PCT = const(100)       # menu button width (percent of screen width)
BTN_WIDTH = SCREEN_WIDTH * BTN_WIDTH_PCT // 100
PIN_BTN_HEIGHT = const(85)       # lock screen PIN keypad button height (px)
PIN_BTN_WIDTH = const(115)       # lock screen PIN keypad button width (px)
BACK_BTN_HEIGHT = const(70)      # back button height (px)
BACK_BTN_WIDTH = const(48)       # back button width (px)
MENU_PCT = const(100)
MENU_WIDTH = SCREEN_WIDTH * MENU_PCT // 100
TITLE_ROW_HEIGHT_PCT = const(8)  # height reserved for the title (percentage of screen height)
TITLE_HEIGHT = TITLE_ROW_HEIGHT_PCT * SCREEN_HEIGHT // 100
TITLE_TA_WIDTH = const(200)      # width of editable title text area (px)
TITLE_PADDING = const(15)        # gap between title row and button container
STATUS_BTN_HEIGHT = const(50)    # status bar button height (was 30)
STATUS_BTN_WIDTH = const(60)     # status bar button width  (was 40)
SWITCH_HEIGHT = const(82)        # toggle switch height (was 55)
SWITCH_WIDTH = const(45)         # toggle switch width  (was 30)
FINGERPRINT_LBL_WIDTH = const(40)  # width of fingerprint labels (px)
FORM_TA_HEIGHT = const(50)       # height of form text area (px)

SMALL_PAD = const(4)
PAD = const(8)
BIG_PAD = const(12)

CARD_H = STATUS_BTN_HEIGHT + 2 * BIG_PAD + 2  # context-bar card height (shared by dropup, seed, wallet)

# --- Status bar / content area layout ---
STATUS_BAR_PCT = const(8)        # navigation bar (bottom), % of screen height
STATUS_BAR_H = SCREEN_HEIGHT * STATUS_BAR_PCT // 100
CONTENT_PCT = 100 - STATUS_BAR_PCT # 100 - STATUS_BAR_PCT (no top bar)
CONTENT_H = SCREEN_HEIGHT * CONTENT_PCT // 100
BATTERY_WIDTH = const(50)        # battery widget width (px)

# --- Navigation history ---
MAX_HISTORY_DEPTH = const(10)      # maximum number of entries in the back-navigation stack

# --- Icon sizes ---
BTC_ICON_WIDTH = const(42)            # layout space per icon (native bitmap size)

# Modal/popup 
MODAL_WIDTH_PCT = const(75)  # width of modals as percentage of screen width
MODAL_WIDTH = SCREEN_WIDTH * MODAL_WIDTH_PCT // 100
MODAL_HEIGHT_PCT = const(75) # height of modals as percentage of screen height
MODAL_HEIGHT = SCREEN_HEIGHT * MODAL_HEIGHT_PCT // 100

# Confirmation slider
CONFIRMATION_SLIDER_HEIGHT = BTN_HEIGHT  # slider height matches button height

# UIExplainer dimensions and style
EXPLAINER_WIDTH_PCT = const(70)   # Width of explainer text box (percentage of screen)
EXPLAINER_WIDTH = SCREEN_WIDTH * EXPLAINER_WIDTH_PCT // 100
EXPLAINER_HEIGHT_PCT = const(40)  # Height of explainer text box (percentage of screen)
EXPLAINER_HEIGHT = SCREEN_HEIGHT * EXPLAINER_HEIGHT_PCT // 100

# Animation constants
ANIM_MS_HORIZONTAL = const(150)   # horizontal slide duration (ms)
ANIM_MS_VERTICAL = const(300)     # vertical slide duration (ms)
GUI_REFRESH_MS = const(2000)      # periodic UI refresh interval (ms)

from micropython import const
import lvgl as lv

BTN_HEIGHT = const(50)
BTN_WIDTH = const(100)  # Percentage of container width
MENU_PCT = const(93)
STATUS_BTN_HEIGHT = const(30)
STATUS_BTN_WIDTH = const(40)
SWITCH_HEIGHT = const(55)
SWITCH_WIDTH = const(30)
PAD_SIZE = const(5)
BTC_ICON_WIDTH = const(24)  # width allocated to BTC icons in buttons
ONE_LETTER_SYMBOL_WIDTH = const(11)  # width allocated to 1-letter status symbols in the status bar
TWO_LETTER_SYMBOL_WIDTH = const(19)  # width allocated to 2-letter status symbols in the status bar
THREE_LETTER_SYMBOL_WIDTH = const(27)  # width allocated to 3-letter status symbols in the status bar

GREEN = const("#00D100")
GREEN_HEX = lv.color_hex(0x00D100)
ORANGE = const("#FF9A00")
ORANGE_HEX = lv.color_hex(0xFF9A00)
RED = const("#F10000")
RED_HEX = lv.color_hex(0xF10000)
WHITE_HEX = lv.color_hex(0xFFFFFF)
BLACK_HEX = lv.color_hex(0x000000)
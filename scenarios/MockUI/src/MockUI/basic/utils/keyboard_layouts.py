"""Keyboard layout key-map constants for KeyboardManager.

Each layout is a tuple of (map_lower, map_upper, map_special, ctrl_text, ctrl_special)
ready to pass to ``lv.keyboard.set_map()``.
"""

import lvgl as lv


def _full_layout():
    ctrl_text = (
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 3, 1, 1, 1,
    )
    map_lower = (
        "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "\n",
        "a", "s", "d", "f", "g", "h", "j", "k", "l", "\n",
        "z", "x", "c", "v", "b", "n", "m", lv.SYMBOL.BACKSPACE, "\n",
        "ABC", "1#", " ", lv.SYMBOL.LEFT, lv.SYMBOL.RIGHT, lv.SYMBOL.OK, "",
    )
    map_upper = (
        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "\n",
        "A", "S", "D", "F", "G", "H", "J", "K", "L", "\n",
        "Z", "X", "C", "V", "B", "N", "M", lv.SYMBOL.BACKSPACE, "\n",
        "abc", "1#", " ", lv.SYMBOL.LEFT, lv.SYMBOL.RIGHT, lv.SYMBOL.OK, "",
    )
    ctrl_special = (
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 3, 1, 1, 1,
    )
    map_special = (
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "\n",
        "!", "@", "#", "$", "%", "&", "*", "(", ")", "_", "\n",
        "-", "+", "=", "?", "/", "[", "]", "{", lv.SYMBOL.BACKSPACE, "\n",
        "ABC", "abc", " ", lv.SYMBOL.LEFT, lv.SYMBOL.RIGHT, lv.SYMBOL.OK, "",
    )
    return map_lower, map_upper, map_special, ctrl_text, ctrl_special


def _alnum_layout():
    ctrl_text = (
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 3, 1, 1, 1,
    )
    map_lower = (
        "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "\n",
        "a", "s", "d", "f", "g", "h", "j", "k", "l", "\n",
        "z", "x", "c", "v", "b", "n", "m", lv.SYMBOL.BACKSPACE, "\n",
        "ABC", "1#", " ", lv.SYMBOL.LEFT, lv.SYMBOL.RIGHT, lv.SYMBOL.OK, "",
    )
    map_upper = (
        "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "\n",
        "A", "S", "D", "F", "G", "H", "J", "K", "L", "\n",
        "Z", "X", "C", "V", "B", "N", "M", lv.SYMBOL.BACKSPACE, "\n",
        "abc", "1#", " ", lv.SYMBOL.LEFT, lv.SYMBOL.RIGHT, lv.SYMBOL.OK, "",
    )
    ctrl_special = (
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 2, 1, 1, 1, 1
    )
    map_special = (
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "\n",
        "ABC", "abc", " ", lv.SYMBOL.LEFT, lv.SYMBOL.RIGHT, lv.SYMBOL.BACKSPACE, lv.SYMBOL.OK, "",
    )
    return map_lower, map_upper, map_special, ctrl_text, ctrl_special

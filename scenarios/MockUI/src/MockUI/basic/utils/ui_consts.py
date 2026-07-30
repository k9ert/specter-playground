from micropython import const


AUTO_GROW_MENU_BUTTONS = const(1) #makes menu elements grow until whole screen is filled

MAX_HISTORY_DEPTH = const(10) # maximum number of entries in the back-navigation stack

GUI_REFRESH_MS = const(2000) # periodic UI refresh interval (ms), mainly for battery status updates

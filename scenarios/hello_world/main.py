# main.py - Frozen Hello World
import udisplay
udisplay.init()

import lvgl as lv

scr = lv.obj()
scr.set_style_bg_color(lv.color_hex(0x000000), 0)
lv.screen_load(scr)

lbl = lv.label(scr)
lbl.set_text("Hello\nWorld!")
lbl.set_style_text_color(lv.color_hex(0xFFFFFF), 0)
lbl.set_style_text_font(lv.font_montserrat_28, 0)
lbl.center()

udisplay.update(30)

# Enable USB REPL
import pyb
pyb.usb_mode("VCP")

import time
while True:
    udisplay.update(30)
    time.sleep_ms(30)

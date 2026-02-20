# main.py - MockUI on STM32F469 Discovery
import gc
import display
import lvgl as lv
import utime as time

from MockUI import NavigationController, SpecterState

# Init display without autoupdate timer to avoid heap fragmentation
display.init()

gc.collect()

lv.theme_default_init(
    None,
    lv.palette_main(lv.PALETTE.BLUE_GREY),
    lv.palette_main(lv.PALETTE.RED),
    True,
    lv.font_montserrat_16,
)

specter_state = SpecterState()
specter_state.has_battery = True
specter_state.battery_pct = 100

specter_state.hasQR = True
specter_state.enabledQR = True

specter_state.hasSD = True
specter_state.enabledSD = False
specter_state.detectedSD = True

specter_state.hasSmartCard = True
specter_state.enabledSmartCard = True
specter_state.detectedSmartCard = True

specter_state.seed_loaded = False
specter_state.active_passphrase = ""
specter_state.pin = "21"

gc.collect()

scr = NavigationController(specter_state)
lv.screen_load(scr)

# Enable USB REPL for debugging
import pyb
pyb.usb_mode("VCP")

while True:
    display.update(30)
    time.sleep_ms(30)

# boot.py -- minimal boot for MockUI firmware
import pyb

# power hold
pwr = pyb.Pin("B15", pyb.Pin.OUT)
pwr.on()

# Import platform to trigger early sdram.init()
import platform

pyb.usb_mode("VCP+MSC") # Enable USB REPL for debugging
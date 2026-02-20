# boot.py -- minimal with platform import for early sdram init
import pyb
pwr = pyb.Pin("B15", pyb.Pin.OUT)
pwr.on()

# Import platform to trigger early sdram.init()
import platform

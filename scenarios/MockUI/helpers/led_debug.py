"""LED debug helpers (4-bit codes on STM32F469 Discovery LEDs)."""

_available = False
_leds = None
_time = None
_last_code = None


def _ensure():
    global _available, _leds, _time
    if _available or _leds is not None:
        return
    try:
        import pyb
        import utime as time

        _leds = [pyb.LED(i) for i in range(1, 5)]
        _time = time
        _available = True
    except Exception:
        _available = False
        _leds = None
        _time = None


def _apply_code(value, on_state=None):
    if not _available or _leds is None:
        return
    for bit, led in enumerate(_leds):
        if value & (1 << bit):
            if on_state is None or on_state:
                led.on()
            else:
                led.off()
        else:
            led.off()


def set_code(code, delay_ms=1000):
    """Show a 4-bit code on the LEDs."""
    _ensure()
    if not _available:
        return
    global _last_code
    _last_code = code
    value = code & 0x0F
    _apply_code(value, on_state=True)
    if _time is not None and delay_ms:
        _time.sleep_ms(delay_ms)


def blink_code(code=None, period_ms=250):
    """Blink a 4-bit code forever."""
    _ensure()
    if not _available:
        return
    if code is None:
        code = _last_code if _last_code is not None else 0
    value = code & 0x0F
    on = False
    while True:
        on = not on
        _apply_code(value, on_state=on)
        if _time is not None:
            _time.sleep_ms(period_ms)

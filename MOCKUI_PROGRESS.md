# MockUI Firmware - Progress & Issues

## Goal
Get the MockUI scenario working as flashable firmware on the STM32F469 Discovery board.

## Status: WORKING

The MockUI firmware boots, displays the full GUI with status bar, icons, menus, and
translated English text on the STM32F469 Discovery board.

## Branch
`fix-mockui-firmware`

## Files Created/Modified
- `scenarios/mockui_fw/boot.py` - Minimal boot with power hold + SDRAM init
- `scenarios/mockui_fw/main.py` - Entry point adapted from `scenarios/mock_ui.py` (simulator)
- `manifests/mockui.py` - Frozen manifest including disco libs, platform, MockUI scenarios
- `Makefile` - Added `mockui` target + `FROZEN_MANIFEST_MOCKUI` variable
- `scenarios/MockUI/basic/symbol_lib/icon.py` - **Fixed**: switched ARGB8888 -> A8 format
- `scenarios/MockUI/src/MockUI/i18n/translations_embedded.py` - **New**: embedded English translations for frozen firmware
- `scenarios/MockUI/src/MockUI/i18n/i18n_manager.py` - **Fixed**: added fallback to embedded translations

## Issues Found & Fixed

### 1. No firmware entry point for MockUI
**Problem**: MockUI only had a simulator entry (`scenarios/mock_ui.py`). No `boot.py`/`main.py` for flashing.
**Solution**: Created `scenarios/mockui_fw/` with proper boot.py (power + SDRAM) and main.py.

### 2. USB REPL disabled by default boot
**Problem**: `boot/main/boot.py` calls `pyb.usb_mode(None)`, killing REPL access.
**Solution**: Custom `boot.py` in `mockui_fw/` that skips USB disabling.

### 3. Missing platform/config in manifest
**Problem**: `platform.py` and `config_default.py` needed for SDRAM init weren't frozen.
**Solution**: Added `freeze('../src', ('platform.py', 'config_default.py'))` to mockui manifest.

### 4. MemoryError: heap fragmentation -- FIXED
**Problem**: `MemoryError: memory allocation failed, allocating 3120 bytes`
- Crash path: `NavigationController.__init__` -> `StatusBar.__init__` -> `BTC_ICONS.UNLOCK.add_to_parent()` -> `create_icon_from_bitmap()` -> `bytes(icon_data_argb)`
- Root cause: `create_icon_from_bitmap()` converts alpha patterns to ARGB8888, requiring 4 bytes/pixel
- For 24x24 icons: 576 pixels x 4 = 2,304 bytes contiguous allocation
- After imports, heap has 135KB free but max contiguous block only ~2,320-3,088 bytes
- The intermediate Python list + final bytes() conversion causes two large allocations

**Memory diagnostics before fix (via REPL)**:
```
GC: total: 245696, used: 110144, free: 135552
No. of 1-blocks: 624, 2-blocks: 202, max blk sz: 113, max free sz: 193
```
Max contiguous: 193 blocks x 16 bytes = 3,088 bytes (too small for 3,120 byte allocation)

**Solution**: Switch from ARGB8888 to A8 (alpha-only) image format in `icon.py`:
- A8 uses 1 byte/pixel instead of 4 (576 bytes vs 2,304 for 24x24)
- The pattern data in `btc_icons.py` is already stored as `bytes([alpha_values...])` -- used directly as A8 image data
- **Zero heap allocation** for pixel data (references frozen bytecode in flash)
- Color applied via LVGL `image_recolor` style property instead of baking into pixels
- Cache simplified: one entry per pattern (color-independent) instead of per (pattern, color)

**After fix**: 122KB free, MockUI boots and renders all icons correctly with colors.

### 5. i18n translations missing -- FIXED
**Problem**: Menu items showed raw translation keys (e.g. `MAIN_MENU_TITLE`) instead of English text.
**Cause**: MicroPython `freeze()` only handles `.py` files; JSON translation files aren't frozen.

**Solution**: Created `translations_embedded.py` with English translations as a Python dict.
Modified `i18n_manager.py` to fall back to embedded translations when JSON files aren't
available (frozen firmware), while still supporting JSON-first loading for the simulator.

**After fix**: All menu items show proper English text.

## Memory Architecture
- STM32F469: 384KB SRAM, 16MB SDRAM
- MicroPython GC heap: ~245KB (internal SRAM)
- After MockUI fully loaded: ~122KB free
- SDRAM used for display framebuffer, not for Python heap

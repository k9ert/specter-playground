# German Umlaut Font Support for MockUI

This directory contains Montserrat fonts extended with German umlaut characters (Ä, Ö, Ü, ä, ö, ü, ß).

## Generated Files

The script `generate_fonts_with_umlauts.sh` generates font files for sizes: 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28.

Each font includes:
- Standard ASCII (0x20-0x7F)
- Degree symbol (°)
- Bullet (•)
- German umlauts: Ä, Ö, Ü, ä, ö, ü, ß

## Options for Using These Fonts in MockUI

### Option 1: Load Fonts Dynamically in MicroPython (RECOMMENDED for Simulator)

**Advantages:**
- No firmware rebuild needed
- Easy to test and iterate
- Works immediately in simulator
- Can switch fonts at runtime

**Implementation:**
1. Compile the C font files to binary format using `lv_font_conv` with `--format bin`
2. Load fonts at runtime using `lv.font_load("path/to/font.bin")`
3. Set the loaded font: `label.set_style_text_font(loaded_font, 0)`

**Example:**
```python
# In mock_ui.py or a font loading module
import lvgl as lv

# Load custom font
font_12_de = lv.font_load("scenarios/MockUI/src/MockUI/fonts/montserrat_12_de.bin")
if font_12_de:
    lv.font_default = font_12_de
```

**Status:** Requires converting .c files to .bin format first.

---

### Option 2: Include in MicroPython C Module (For Hardware)

**Advantages:**
- Fonts compiled into firmware
- No runtime loading overhead
- Better for production hardware

**Implementation:**
1. Add the generated .c files to `f469-disco/usermods/udisplay_f469/`
2. Create a Python binding to expose the fonts
3. Update the module's `mp_obj_module_t` to include the fonts
4. Rebuild MicroPython firmware

**Example structure:**
```c
// In a new file: f469-disco/usermods/udisplay_f469/lv_fonts_de.c
#include "py/obj.h"
#include "lvgl/lvgl.h"

// Include generated fonts
LV_FONT_DECLARE(montserrat_12_de);
LV_FONT_DECLARE(montserrat_16_de);

// Export to Python
MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_font_montserrat_12_de_type, ...
);
```

**Status:** Requires C module development and firmware rebuild.

---

### Option 3: Replace Default LVGL Fonts (For Hardware)

**Advantages:**
- Seamless integration
- No code changes needed
- All existing code automatically uses new fonts

**Implementation:**
1. Copy generated .c files to `f469-disco/usermods/udisplay_f469/lvgl/src/font/`
2. Update `lv_conf.h` to use new font names instead of defaults
3. Rebuild firmware

**Changes needed in lv_conf.h:**
```c
// OLD:
#define LV_FONT_MONTSERRAT_12 1
#define LV_FONT_MONTSERRAT_16 1

// NEW:
#define LV_FONT_MONTSERRAT_12 0  // Disable default
#define LV_FONT_MONTSERRAT_16 0  // Disable default

// Then manually include in lv_font.c:
LV_FONT_DECLARE(montserrat_12_de);
LV_FONT_DECLARE(montserrat_16_de);
```

**Status:** Simplest for hardware but requires firmware rebuild.

---

### Option 4: Python Font Wrapper Module (For Simulator)

**Advantages:**
- Pure Python solution
- No C compilation needed
- Can be used immediately in simulator

**Implementation:**
1. Create a Python module that loads binary fonts at startup
2. Provide helper functions to get fonts by size
3. Monkey-patch LVGL's font access

**Example:**
```python
# scenarios/MockUI/src/MockUI/fonts/font_loader.py
import lvgl as lv
import os

class FontLoaderDE:
    def __init__(self):
        self.fonts = {}
        self._load_fonts()
    
    def _load_fonts(self):
        font_dir = os.path.dirname(__file__)
        for size in [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]:
            font_path = f"{font_dir}/montserrat_{size}_de.bin"
            if os.path.exists(font_path):
                self.fonts[size] = lv.font_load(font_path)
    
    def get_font(self, size):
        return self.fonts.get(size)

font_loader_de = FontLoaderDE()
```

**Status:** Requires .bin format conversion first.

---

## Recommended Approach

### For Simulator Testing (MockUI):
**Option 1 or 4** - Dynamic loading allows quick iteration without rebuilding firmware.

### For Hardware Deployment:
**Option 3** - Replacing default fonts is cleanest and requires no code changes in MockUI.

## Implementation Status

### ✅ Option 1 - IMPLEMENTED (For Simulator)

Binary fonts have been generated and a Python font loader module is ready to use.

**Files created:**
- `generate_binary_fonts.sh` - Script to generate .bin font files
- `montserrat_<size>_de.bin` - Binary font files (11 sizes)
- `font_loader_de.py` - Python module for loading fonts
- `__init__.py` - Package initialization

**Usage in MockUI:**

```python
from scenarios.MockUI.fonts import font_loader_de

# Initialize fonts (happens automatically on import)
# Prints loading status to console

# Get a specific font size
font_12 = font_loader_de.get_font(12)
font_16 = font_loader_de.get_font(16)

# Use the font on a label or other widget
label.set_style_text_font(font_12, 0)

# Check available sizes
print(f"Available sizes: {font_loader_de.get_available_sizes()}")
```

**Integration into mock_ui.py:**

Add after LVGL initialization:

```python
import lvgl as lv
from scenarios.MockUI.fonts import font_loader_de

# ... existing code ...

# Load German umlaut fonts
print("Loading German umlaut fonts...")

# Set size 12 for status bar (or size 16 as default theme)
font_12 = font_loader_de.get_font(12)
font_16 = font_loader_de.get_font(16)

if font_16:
    # Update the default theme font
    theme = lv.theme_default_init(
        lv.disp_get_default(),
        lv.palette_main(lv.PALETTE.BLUE),
        lv.palette_main(lv.PALETTE.RED),
        True,
        font_16  # Use German umlaut font
    )
```

**Testing:**

Run the simulator and check console output for font loading status:

```bash
sudo --preserve-env=XDG_RUNTIME_DIR nix develop -c make simulate SCRIPT=mock_ui.py
```

Expected output:
```
FontLoaderDE: Loaded 11/11 German umlaut fonts
```

---

## Next Steps

1. **For simulator (current setup):**
   - Integrate `font_loader_de` into `mock_ui.py` or `SpecterGui`
   - Update status bar and other components to use German fonts
   - Test German text rendering with umlauts

2. **For firmware integration (future):** Follow Option 2 or 3 implementation guides above

## Regenerating Fonts

To regenerate the fonts (e.g., to add more characters):

```bash
cd scenarios/MockUI/src/MockUI/fonts
./generate_fonts_with_umlauts.sh
```

To add more characters, edit the `CHAR_RANGE` variable in the script.

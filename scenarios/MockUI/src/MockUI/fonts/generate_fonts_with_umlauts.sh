#!/bin/bash
# Generate Montserrat fonts with German umlaut support
# This script creates font files with extended character support without modifying LVGL defaults

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR"
SOURCE_FONT_DIR="$SCRIPT_DIR/../../../f469-disco/usermods/udisplay_f469/lvgl/scripts/built_in_font"
SOURCE_FONT="$SOURCE_FONT_DIR/Montserrat-Medium.ttf"

# Character ranges:
# 0x20-0x7F = Standard ASCII
# 0xB0 = Degree symbol (°)
# 0x2022 = Bullet (•)
# 0xC4 = Ä, 0xD6 = Ö, 0xDC = Ü
# 0xE4 = ä, 0xF6 = ö, 0xFC = ü
# 0xDF = ß (German sharp s)
# 61441-63650 = LVGL FontAwesome symbols (see lv_symbol_def.h)
CHAR_RANGE="0x20-0x7F,0xB0,0x2022,0xC4,0xD6,0xDC,0xE4,0xF6,0xFC,0xDF,61441,61448,61451,61452,61453,61457,61459,61461,61465,61468,61473,61478,61479,61480,61502,61507,61512,61515,61516,61517,61521,61522,61523,61524,61543,61544,61550,61552,61553,61556,61559,61560,61561,61563,61587,61589,61636,61637,61639,61641,61664,61671,61674,61683,61724,61732,61787,61931,62016,62017,62018,62019,62020,62087,62099,62189,62212,62810,63426,63650"

echo "================================"
echo "Montserrat Font Generator"
echo "with German Umlaut Support"
echo "================================"
echo ""
echo "Source font: $SOURCE_FONT"
echo "Output directory: $OUTPUT_DIR"
echo "Character range: $CHAR_RANGE"
echo ""

# Check if source font exists
if [ ! -f "$SOURCE_FONT" ]; then
    echo "ERROR: Source font not found: $SOURCE_FONT"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Font sizes used in MockUI
FONT_SIZES=(8 10 12 14 16 18 20 22 24 26 28)

echo "Generating fonts..."
echo ""

for SIZE in "${FONT_SIZES[@]}"; do
    OUTPUT_FILE="$OUTPUT_DIR/montserrat_${SIZE}_de.c"
    
    echo "Generating size $SIZE → $(basename $OUTPUT_FILE)"
    
    lv_font_conv \
        --no-compress \
        --no-prefilter \
        --bpp 4 \
        --size "$SIZE" \
        --font "$SOURCE_FONT" \
        --range "$CHAR_RANGE" \
        --format lvgl \
        --force-fast-kern-format \
        --lv-font-name "montserrat_${SIZE}_de" \
        -o "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Success"
    else
        echo "  ✗ Failed"
        exit 1
    fi
done

echo ""
echo "================================"
echo "Font generation complete!"
echo "================================"
echo ""
echo "Generated files:"
ls -lh "$OUTPUT_DIR"/*.c 2>/dev/null || echo "No .c files found"
echo ""
echo "Next steps:"
echo "1. Include the generated font .c files in your MicroPython build"
echo "2. Update the font loading code to use these new fonts"
echo "3. Rebuild the firmware"

#!/bin/bash
# Convert .c font files to .bin format for dynamic loading in LVGL

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR"
FONT_DIR="$SCRIPT_DIR/../../../f469-disco/usermods/udisplay_f469/lvgl/scripts/built_in_font"
SOURCE_FONT="$FONT_DIR/Montserrat-Medium.ttf"
SYMBOL_FONT="$FONT_DIR/FontAwesome5-Solid+Brands+Regular.woff"

# Character ranges:
# Text chars from Montserrat
TEXT_RANGE="0x20-0x7F,0xB0,0x2022,0xC4,0xD6,0xDC,0xE4,0xF6,0xFC,0xDF"
# Symbol chars from FontAwesome (LVGL symbols)
SYMBOL_RANGE="61441,61448,61451,61452,61453,61457,61459,61461,61465,61468,61473,61478,61479,61480,61502,61507,61512,61515,61516,61517,61521,61522,61523,61524,61543,61544,61550,61552,61553,61556,61559,61560,61561,61563,61587,61589,61636,61637,61639,61641,61664,61671,61674,61683,61724,61732,61787,61931,62016,62017,62018,62019,62020,62087,62099,62189,62212,62810,63426,63650"

echo "================================"
echo "Montserrat Binary Font Generator"
echo "with German Umlaut + LVGL Symbols"
echo "================================"
echo ""
echo "Text font: $SOURCE_FONT"
echo "Symbol font: $SYMBOL_FONT"
echo "Output directory: $OUTPUT_DIR"
echo "Text range: $TEXT_RANGE"
echo "Symbol range: LVGL FontAwesome symbols"
echo ""

# Check if source fonts exist
if [ ! -f "$SOURCE_FONT" ]; then
    echo "ERROR: Source font not found: $SOURCE_FONT"
    exit 1
fi

if [ ! -f "$SYMBOL_FONT" ]; then
    echo "ERROR: Symbol font not found: $SYMBOL_FONT"
    exit 1
fi

# Font sizes used in MockUI
FONT_SIZES=(8 10 12 14 16 18 20 22 24 26 28)

echo "Generating binary fonts..."
echo ""

for SIZE in "${FONT_SIZES[@]}"; do
    OUTPUT_FILE="$OUTPUT_DIR/montserrat_${SIZE}_de.bin"
    
    echo "Generating size $SIZE → $(basename $OUTPUT_FILE)"
    
    # Use both fonts: Montserrat for text, FontAwesome for symbols
    lv_font_conv \
        --no-compress \
        --no-prefilter \
        --bpp 4 \
        --size "$SIZE" \
        --font "$SOURCE_FONT" --range "$TEXT_RANGE" \
        --font "$SYMBOL_FONT" --range "$SYMBOL_RANGE" \
        --format bin \
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
echo "Binary font generation complete!"
echo "================================"
echo ""
echo "Generated files:"
ls -lh "$OUTPUT_DIR"/*.bin 2>/dev/null || echo "No .bin files found"
echo ""
echo "Next steps:"
echo "1. Use font_loader_de.py to load these fonts in MockUI"
echo "2. Run the simulator to test German umlaut rendering"

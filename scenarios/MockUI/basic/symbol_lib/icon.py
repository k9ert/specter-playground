"""Core Icon class and bitmap conversion utilities."""

import lvgl as lv
from ..ui_consts import WHITE_HEX


def color_to_rgb(color):
    """
    Extract RGB values from an LVGL color object.
    
    Args:
        color: lv.color_t object (e.g., from lv.color_hex(0xFF0000)) or integer
    
    Returns:
        tuple: (r, g, b) values as integers (0-255)
    """
    try:
        # Try to get RGB values from color object methods/attributes
        r = color.red() if callable(getattr(color, 'red', None)) else color.red
        g = color.green() if callable(getattr(color, 'green', None)) else color.green
        b = color.blue() if callable(getattr(color, 'blue', None)) else color.blue
    except (AttributeError, TypeError):
        # Fallback: if it's already an integer, extract RGB
        color_int = int(color)
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
    
    return (r, g, b)


def create_icon_from_bitmap(pattern, width, height):
    """
    Convert an alpha-channel bitmap pattern to A8 format for LVGL.

    Uses A8 (alpha-only) format to minimise memory allocation.
    For 8-bit patterns already stored as ``bytes``, the data is used
    directly with zero heap allocation (references frozen bytecode).
    Color is applied separately via the image recolor style.

    Args:
        pattern: bytes or list of alpha values (0-255) for each pixel, or
                 list of 0s and 1s for legacy binary patterns
        width: Width of the icon in pixels
        height: Height of the icon in pixels

    Returns:
        lv.image_dsc_t object ready to use with lv.image
    """
    # Validate pattern size matches expected dimensions
    expected_size = width * height
    if len(pattern) != expected_size:
        raise ValueError(
            f"Pattern size mismatch: got {len(pattern)} pixels, "
            f"expected {expected_size} (width={width} × height={height})"
        )

    # Detect if pattern is legacy binary (only 0 and 1) or 8-bit alpha
    max_value = max(pattern) if pattern else 0
    is_binary = max_value <= 1

    if is_binary:
        # Convert binary (0/1) to full alpha (0x00/0xFF)
        icon_data_bytes = bytes(0xFF if a else 0x00 for a in pattern)
    elif isinstance(pattern, bytes):
        # 8-bit alpha already in bytes — use directly (zero copy from flash)
        icon_data_bytes = pattern
    else:
        # List of 8-bit alpha values — convert once
        icon_data_bytes = bytes(pattern)

    # Create LVGL image descriptor with A8 (alpha-only) format
    return lv.image_dsc_t({
        'header': {
            'w': width,
            'h': height,
            'cf': lv.COLOR_FORMAT.A8,
        },
        'data_size': len(icon_data_bytes),
        'data': icon_data_bytes,
    })


class Icon:
    """
    Reusable icon class that can be rendered as an image.
    
    Can be called with a color to create a new Icon with that color:
        icon = BTC_ICONS.CHECKMARK(GREEN_HEX)
    
    Or used directly (will use white as default color):
        icon = BTC_ICONS.CHECKMARK
    
    NOTE: Unlike lv.SYMBOL.*, custom bitmap icons cannot be directly concatenated 
    into strings because they're images, not font characters. Use create_image() 
    to add icons to buttons/containers with flex layout alongside labels.
    """
    
    # Class-level cache shared across all Icon instances
    # Key: (pattern_id, color_string) -> Value: lv.image_dsc_t
    _global_image_dsc_cache = {}
    
    def __init__(self, pattern, width, height, color=None):
        """
        Initialize an icon with a bitmap pattern.
        
        Args:
            pattern: bytes or list of alpha values (0-255) for each pixel,
                    or list of 0s and 1s for legacy binary patterns
            width: Width of the icon in pixels
            height: Height of the icon in pixels
            color: Optional lv.color_t object (defaults to WHITE_HEX)
        """
        self.pattern = pattern
        self.width = width
        self.height = height
        self.color = color if color is not None else WHITE_HEX
    
    def __call__(self, color):
        """
        Create a new Icon instance with the specified color.
        Reuses the same pattern data.
        
        Args:
            color: lv.color_t object (e.g., from lv.color_hex(0xFF0000))
        
        Returns:
            New Icon instance with the specified color
        """
        return Icon(self.pattern, self.width, self.height, color)
    
    def get_image_dsc(self):
        """
        Get an lv.image_dsc_t for this icon.
        Results are cached in the global cache to avoid recreating descriptors.
        With A8 format the descriptor is colour-independent, so one cached
        entry per unique pattern is sufficient.

        Returns:
            lv.image_dsc_t object
        """
        cache_key = id(self.pattern)

        if cache_key not in Icon._global_image_dsc_cache:
            Icon._global_image_dsc_cache[cache_key] = create_icon_from_bitmap(
                self.pattern, self.width, self.height
            )

        return Icon._global_image_dsc_cache[cache_key]

    def add_to_parent(self, parent):
        """
        Add this icon to a parent lv.image object.
        Sets the A8 image source and applies the icon colour via the
        LVGL ``image_recolor`` style property.

        Args:
            parent: The lv.image object to configure
        """
        parent.set_src(self.get_image_dsc())
        parent.set_size(self.width, self.height)
        # Apply colour via recolor (image data is alpha-only A8)
        r, g, b = color_to_rgb(self.color)
        parent.set_style_image_recolor(lv.color_make(r, g, b), 0)
        parent.set_style_image_recolor_opa(lv.OPA.COVER, 0)

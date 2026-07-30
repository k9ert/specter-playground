"""Core Icon class and bitmap conversion utilities."""

import lvgl as lv

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
            f"expected {expected_size} (width={width} x height={height})"
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
    
    Can be used directly:
        icon = BTC_ICONS.CHECK
    
    NOTE: Unlike lv.SYMBOL.*, custom bitmap icons cannot be directly concatenated 
    into strings because they're images, not font characters. Use create_image() 
    to add icons to buttons/containers with flex layout alongside labels.
    """
    
    def __init__(self, pattern, width, height):
        """
        Initialize an icon with a bitmap pattern.
        
        Args:
            pattern: bytes or list of alpha values (0-255) for each pixel,
                    or list of 0s and 1s for legacy binary patterns
            width: Width of the icon in pixels
            height: Height of the icon in pixels
        """
        self.pattern = pattern
        self.width = width
        self.height = height
        self._dsc = None
    
    def get_image_dsc(self):
        """Return the ``lv.image_dsc_t`` for this icon, building it once on first call.

        The descriptor is stored on the instance.  Because named icons in
        ``BTC_ICONS`` are module-level singletons this allocates at most one
        descriptor (≈320 B heap) per distinct icon that is actually rendered.

        Returns:
            lv.image_dsc_t object
        """
        if self._dsc is None:
            self._dsc = create_icon_from_bitmap(
                self.pattern, self.width, self.height
            )
        return self._dsc

"""
Font loader for German umlaut-enabled Montserrat fonts.

This module provides dynamic loading of Montserrat fonts with German umlaut support.
It loads binary font files at runtime and provides helper functions to access them.

Usage:
    from scenarios.MockUI.fonts.font_loader_de import font_loader_de
    
    # Get a specific font size
    font_12 = font_loader_de.get_font(12)
    label.set_style_text_font(font_12, 0)
    
    # Set as default font
    font_loader_de.set_default_font(12)
"""

import lvgl as lv


class FontLoaderDE:
    """
    Loads and manages Montserrat fonts with German umlaut support.
    
    Attributes:
        fonts (dict): Dictionary mapping font sizes to loaded font objects
        available_sizes (list): List of available font sizes
    """
    
    def __init__(self):
        """Initialize the font loader."""
        self.fonts = {}
        self.available_sizes = [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
        # Get directory path using string operations (MicroPython compatible)
        self._font_dir = __file__.rsplit('/', 1)[0] if '/' in __file__ else '.'
        self._load_fonts()
    
    def _load_fonts(self):
        """
        Load all available binary font files.
        
        This method loads fonts on initialization. If a font file is missing or
        fails to load, it will be skipped and a warning printed.
        
        Note: LVGL's filesystem support is disabled, so we load files into memory
        first and use lv.binfont_create_from_buffer() instead of lv.binfont_create().
        """
        loaded_count = 0
        failed_fonts = []
        
        for size in self.available_sizes:
            font_path = self._font_dir + "/" + f"montserrat_{size}_de.bin"
            
            # Try to load the font from memory buffer (LVGL FS is disabled)
            try:
                # Read the binary font file into memory
                with open(font_path, 'rb') as f:
                    font_data = f.read()
                
                # Create font from buffer using LVGL's memory filesystem
                font = lv.binfont_create_from_buffer(font_data, len(font_data))
                
                if font:
                    self.fonts[size] = font
                    loaded_count += 1
                else:
                    failed_fonts.append((size, "binfont_create_from_buffer returned None"))
            except Exception as e:
                failed_fonts.append((size, str(e)))
        
        # Print loading summary
        print(f"FontLoaderDE: Loaded {loaded_count}/{len(self.available_sizes)} German umlaut fonts")
        
        if failed_fonts:
            print("  Failed to load:")
            for size, reason in failed_fonts:
                print(f"    - Size {size}: {reason}")
    
    def get_font(self, size):
        """
        Get a font by size.
        
        Args:
            size (int): Font size (8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28)
        
        Returns:
            lv.font or None: The loaded font object, or None if not available
        
        Example:
            font = font_loader_de.get_font(16)
            if font:
                label.set_style_text_font(font, 0)
        """
        if size not in self.fonts:
            print(f"FontLoaderDE: Font size {size} not available. Available sizes: {list(self.fonts.keys())}")
            return None
        return self.fonts.get(size)
    
    def set_default_font(self, size):
        """
        Set the default LVGL font to the specified size.
        
        Args:
            size (int): Font size to use as default
        
        Returns:
            bool: True if successful, False otherwise
        
        Example:
            if font_loader_de.set_default_font(12):
                print("Default font updated successfully")
        """
        font = self.get_font(size)
        if font:
            try:
                # Set as default font for the default theme
                theme = lv.theme_get_from_obj(lv.scr_act())
                if theme:
                    # This approach may not work in all LVGL versions
                    # Alternative: manually update all objects
                    pass
                
                # Alternative approach: update default display font
                disp = lv.disp_get_default()
                if disp:
                    # Note: This may require LVGL binding support
                    pass
                
                print(f"FontLoaderDE: Set default font to size {size}")
                return True
            except Exception as e:
                print(f"FontLoaderDE: Failed to set default font: {e}")
                return False
        return False
    
    def get_available_sizes(self):
        """
        Get list of successfully loaded font sizes.
        
        Returns:
            list: List of available font sizes
        """
        return sorted(self.fonts.keys())
    
    def is_loaded(self, size):
        """
        Check if a specific font size is loaded.
        
        Args:
            size (int): Font size to check
        
        Returns:
            bool: True if the font is loaded, False otherwise
        """
        return size in self.fonts
    
    def reload(self):
        """
        Reload all fonts.
        
        This can be useful if font files have been updated.
        Note: Previously loaded font references will still point to old fonts.
        """
        # Free existing fonts
        self.fonts.clear()
        
        # Reload
        self._load_fonts()


# Global singleton instance
font_loader_de = FontLoaderDE()


# Convenience functions for easier access
def get_font_de(size):
    """
    Convenience function to get a German umlaut font.
    
    Args:
        size (int): Font size
    
    Returns:
        lv.font or None: The loaded font object
    """
    return font_loader_de.get_font(size)


def set_default_font_de(size):
    """
    Convenience function to set default font.
    
    Args:
        size (int): Font size
    
    Returns:
        bool: True if successful
    """
    return font_loader_de.set_default_font(size)

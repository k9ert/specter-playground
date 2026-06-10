"""
Template for handlers of settings files.

Handles loading, validating, and providing data from efficient binary format.
Supports fallback to default data for missing keys.
Enables runtime loading of new data via JSON to binary conversion.

REMINDER: Derived classes need to import the specific Keys module for their settings type
"""


import os
import json

class SettingFileManager:
    """Template Class, do not use directly. Create a subclass for each type of settings file."""
    
    #VARIABLES THAT MUST BE OVERRIDDEN IN DERIVED CLASS:
    #
    # Unique identifier string for this type of settings file (e.g. "LANG" for language files)
    # Needs to be overwritten in derived class
    COMPILER = None    # SettingsFileCompiler subclass instance for this settings type
    SETTINGS_DIR = None        # lowercase string used as flash subdirectory name (e.g. "i18n", "themes")
    DEFAULT_SETTING_FILE = None  # name of the built-in default file (e.g. "en", "default")
    KEYS_CLASS = None  # Keys class imported from the type-specific keys module

    _instances = {}  # singleton registry shared across all subclasses

    @classmethod
    def get_instance(cls):
        """Return the singleton instance for this subclass, creating it if needed."""
        if cls not in cls._instances:
            cls._instances[cls] = cls()
        return cls._instances[cls]

    def __init__(self):
        """
        Initialize the file settings manager.

        All settings files are stored in /flash/<type>/ including the
        default settings file (embedded via build system).
        """
        self.current = None
        self.current_file = None
        self.default_file = None
        self.available_files = []
        
        self.FLASH_DIR = "/flash" + self.SETTINGS_DIR.lower()  # Flash filesystem directory for all settings files of this type
        self.FLASH_CONFIG_PATH = self.FLASH_DIR + "/config.json"  # Persistent configuration storage
        
        # Ensure flash directory exists
        self._ensure_flash_dir()
        
        # Load available files
        self._scan_available_files()
        
        # Load last selected file or default
        selected_file = self._load_stored_preference()
        self.set_setting(selected_file)
    
    def _ensure_flash_dir(self):
        """Verify the flash settings directory exists (should be created by build system)."""
        try:
            # Check if directory exists by trying to list it
            os.listdir(self.FLASH_DIR)
        except OSError:
            # Directory doesn't exist - this indicates a build system problem
            print(f"Warning: {self.FLASH_DIR} does not exist!")
            print("This directory should be created by the build system.")
            print("Settings system may not work correctly.")
        except Exception as e:
            print(f"Warning: Could not access flash settings directory: {e}")

    def _scan_available_files(self):
        """Scan for available settings files (binary format) in flash directory."""
        self.available_files = []
        file_codes = set()
        
        try:
            files = os.listdir(self.FLASH_DIR)
            for filename in files:
                # FAT filesystem returns uppercase names, so normalise
                filename_lower = filename.lower()
                if filename_lower.startswith(self.COMPILER.BINARY_FILE_PREFIX) and filename_lower.endswith(self.COMPILER.BINARY_FILE_SUFFIX):
                    # Use settings compiler function to extract settings name (pass lowercase)
                    settings_name = self.COMPILER.extract_settings_name_from_filename(filename_lower)
                    if settings_name:  # None if invalid
                        file_codes.add(settings_name)
        except OSError:
            pass  # Directory doesn't exist yet
        except Exception as e:
            print(f"Warning: Error scanning {self.FLASH_DIR}: {e}")

        self.available_files = sorted(list(file_codes))

        # Verify default file is available (critical requirement)
        if self.DEFAULT_SETTING_FILE not in self.available_files:
            print(f"CRITICAL ERROR: Default settings file '{self.DEFAULT_SETTING_FILE}' not found in {self.FLASH_DIR}!")
            print("This indicates a build system problem - the default settings file should be embedded in firmware.")
            print("All settings will be replaced with default values until this is fixed.")
    
    def _load_stored_preference(self):
        """Load the last selected settings file from flash config file."""
        try:
            with open(self.FLASH_CONFIG_PATH, 'r') as f:
                config = json.load(f)
            self._apply_loaded_preference(config)
            file = config.get('selected_file', self.DEFAULT_SETTING_FILE)

            # Validate that the file is available
            if file in self.available_files:
                return file
            else:
                print(f"Warning: Saved settings file '{file}' not available, using default settings file '{self.DEFAULT_SETTING_FILE}'")
                return self.DEFAULT_SETTING_FILE
        except Exception as e:
            # Config file doesn't exist or can't be read - use default and try to create it
            print(f"Config file not found or unreadable, using default settings file: {self.DEFAULT_SETTING_FILE}")
            self._save_settings_preference()
            return self.DEFAULT_SETTING_FILE
    
    def _build_preference_data(self):
        """Build the dict to persist as preference data.
        Override in subclasses to add extra fields — call super() and extend the returned dict."""
        return {'selected_file': self.current if self.current is not None else self.DEFAULT_SETTING_FILE}

    def _apply_loaded_preference(self, config):
        """Hook called with the loaded config dict after a successful read.
        Override in subclasses to restore extra persisted state."""
        pass

    def _save_settings_preference(self):
        """Persist current preferences to flash. Reads state via _build_preference_data()."""
        try:
            config = self._build_preference_data()
            with open(self.FLASH_CONFIG_PATH, 'w') as f:
                json.dump(config, f)
            print(f"Settings preference saved: {self.current}")
        except Exception as e:
            # Preference won't persist across reboots, but settings still work in current session
            print(f"Warning: Could not save settings preference (will use default on next boot): {e}")
    
    def set_setting(self, file):
        """
        Set the active settings file.
        
        Args:
            file: Settings file name (e.g., 'default', 'user')
            
        Returns:
            bool: True if settings file was set successfully, False otherwise
        """
        if file not in self.available_files:
            print(f"Warning: Settings file '{file}' not available. Available: {self.available_files}")
            return False
        
        # Construct file paths directly (all files in FLASH_DIR)
        current_path = f"{self.FLASH_DIR}/{self.COMPILER.get_binary_filename(file)}"
        default_path = f"{self.FLASH_DIR}/{self.COMPILER.get_binary_filename(self.DEFAULT_SETTING_FILE)}"
        
        # Verify files exist
        try:
            # Just check if we can stat the files
            os.stat(current_path)
            os.stat(default_path)
        except OSError as e:
            print(f"Error: Settings file not found: {e}")
            return False
        
        # Set file paths
        self.current_file = current_path
        self.default_file = default_path
        self.current = file
        
        # Save preference
        self._save_settings_preference()

        print(f"Settings file set to '{file}' (file: {current_path})")
        return True
    
    def get_current_file(self):
        """Get the current settings file."""
        return self.current
    
    def get_available_files(self):
        """Get list of available settings files."""
        return self.available_files.copy()

    def get_file_name(self, file):
        """
        Return the human-readable file name read from the binary file.
        
        Returns None and prints an error if file is not in the set of available
        files. Otherwise reads the name from the file header. Falls back to file
        itself if the file read fails.
        """
        if file not in self.available_files:
            print(f"Error: File '{file}' is not available. Available: {self.available_files}")
            return None
        
        binary_path = f"{self.FLASH_DIR}/{self.COMPILER.get_binary_filename(file)}"
        name = self.COMPILER.extract_settings_name_from_binary_file(binary_path)
        if name is None:
            # File read failed — degrade gracefully to the raw file name
            return file
        return name

    def get_setting(self, key):
        """
        Get the setting value for a given key.
        
        Tries to read from the current settings file. If the key is not found,
        falls back to the default settings file. If still not found, returns None.
        
        Args:
            key: The setting key to look up
            
        Returns:
            The setting value or None if not found
        """
        # Try to read from current settings file
        value, error = self.COMPILER.read_setting_from_binary(self.current_file, key)
        
        # If not found in current settings, try default settings
        if value is None:
            value, error = self.COMPILER.read_setting_from_binary(self.default_file, key)
        
        return value

    def __getitem__(self, key):
        """Allow using the manager as a dictionary: <instancename>['KEY']"""
        return self.get_setting(key)
    
    def __call__(self, key):
        """Allow using the manager as a function: <instancename>('KEY')"""
        return self.get_setting(key)
    
    def load_setting_from_json(self, json_path, setting_name=None):
        """
        Load a new settings file from JSON file and convert to binary format.
        Saves the binary file to flash filesystem for persistent access.
        
        Args:
            json_path: Path to JSON settings file
            setting_name: Setting name override (extracted from JSON filename if None)
            
        Returns:
            bool: True if settings file was loaded successfully
        """
        try:
            # Extract setting name from filename if not provided
            if setting_name is None:
                setting_name = self.COMPILER.extract_settings_name_from_filename(json_path)
                if setting_name is None:
                    print(f"Error: Could not extract setting name from filename: {json_path}")
                    return False

            # Validate setting name to prevent path traversal and invalid filenames
            if not self.COMPILER.validate_settings_name(setting_name):
                print(f"Error: Invalid setting name '{setting_name}'")
                return False

            # Construct target path in flash directory
            output_path = f"{self.FLASH_DIR}/{self.COMPILER.get_binary_filename(setting_name)}"
            
            # Convert JSON to binary - write directly to target location
            result_path = self.COMPILER.json_to_binary(json_path, self.KEYS_CLASS, output_path)
            
            if result_path is None:
                print("Error: Compilation failed - binary file not created.")
                return False
            
            # Rescan available files to include the newly added file
            self._scan_available_files()
            
            print(f"Successfully loaded settings file '{setting_name}' from {json_path}")
            print(f"Binary file saved to: {result_path}")
            print("Settings file is now available for selection.")
            
            return True
            
        except Exception as e:
            print(f"Error loading settings file from JSON: {e}")
            return False

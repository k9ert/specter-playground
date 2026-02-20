# Next Steps / Open Tasks

1. **SD Card handling**

   - Add backend code + UI for loading language files (JSON) from SD card
   - "Load Language" should self-detect if files mathcing naming cnvention are availbel and offer only valid options
   - Add UI for deleting loaded languages with confirmation and default protection (cannot delete default language)
   - Implement disk space checking before loading new language to prevent out-of-space issues

2. **DISCO TOOL Integration**
   - Update `DISCO_SCRIPT` in `scenarios/MockUI/tests_device/conftest.py` (and tests in general) once disco is merged

3. **Language file versioning**

- Language file versioning/migration system to handle future changes in translation keys without breaking existing language files

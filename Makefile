TARGET_DIR = bin
BOARD ?= STM32F469DISC
FLAVOR ?= SPECTER
USER_C_MODULES ?= ../../../usermods
MPY_DIR ?= f469-disco/micropython
FROZEN_MANIFEST_DISCO ?= ../../../../manifests/disco.py
FROZEN_MANIFEST_DEBUG ?= ../../../../manifests/debug.py
FROZEN_MANIFEST_UNIX ?= ../../../../manifests/unix.py
FROZEN_MANIFEST_PLAYGROUND ?= ../../../../manifests/playground.py
FROZEN_MANIFEST_HELLO ?= ../../../../manifests/hello.py
FROZEN_MANIFEST_MOCKUI ?= ../../../../manifests/mockui.py
DEBUG ?= 0
USE_DBOOT ?= 0
ADD_LANG ?=
ADD_THEME ?=

# Validate ADD_LANG to prevent shell injection (only lowercase letters and commas allowed)
ifneq ($(ADD_LANG),)
ifneq ($(shell echo "$(ADD_LANG)" | grep -E '^[a-z,]+$$'),$(ADD_LANG))
$(error ADD_LANG contains invalid characters. Use only lowercase letters and commas, e.g. ADD_LANG=de,fr)
endif
endif

# Validate ADD_THEME to prevent shell injection (lowercase letters, digits, underscores and commas)
ifneq ($(ADD_THEME),)
ifneq ($(shell echo "$(ADD_THEME)" | grep -E '^[a-z0-9_,]+$$'),$(ADD_THEME))
$(error ADD_THEME contains invalid characters. Use only lowercase letters, digits, underscores and commas, e.g. ADD_THEME=ocean)
endif
endif

$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

# check submodules
$(MPY_DIR)/mpy-cross/Makefile:
	git submodule update --init --recursive

# Sync JSON language files with source code (dry run — warns about drift,
# does NOT modify files; run 'python3 tools/sync_i18n.py' manually to apply)
sync-i18n:
	@echo Checking i18n language files for sync with source code...
	@mkdir -p build
	python3 tools/sync_i18n.py --dry-run

# Icon tree-shaking: remove unused BTC_ICONS from the firmware freeze path.
# Moves unused icon files to tools/symbol_lib/icons_available/ and comments
# them out in btc_icons.py.  Only needed for hardware builds (the simulator
# has no flash-size constraint).  Run manually with --dry-run to preview:
#   python3 tools/symbol_lib/trim_btc_icons.py --dry-run
trim-icons:
	@echo Trimming unused BTC_ICONS from firmware freeze path...
	@mkdir -p build
	python3 tools/symbol_lib/trim_btc_icons.py

# i18n compilation
build-i18n: sync-i18n
	@echo Building i18n files...
	@mkdir -p build/flash_image/i18n
	@cd scenarios/MockUI/src/MockUI/basic/i18n && python3 lang_compiler.py generate_keys languages/specter_ui_en.json translation_keys.py
	@cd scenarios/MockUI/src/MockUI/basic/i18n && python3 lang_compiler.py compile languages/specter_ui_en.json translation_keys.py && mv lang_en.bin ../../../../../../build/flash_image/i18n/
	@if [ -n "$(ADD_LANG)" ]; then \
		for lang in $(shell echo $(ADD_LANG) | tr ',' ' '); do \
			if [ -f scenarios/MockUI/src/MockUI/basic/i18n/languages/specter_ui_$$lang.json ]; then \
				echo "  Compiling $$lang..."; \
				cd scenarios/MockUI/src/MockUI/basic/i18n && python3 lang_compiler.py compile languages/specter_ui_$$lang.json translation_keys.py && mv lang_$$lang.bin ../../../../../../build/flash_image/i18n/ || true; \
			else \
				echo "  Warning: Language file languages/specter_ui_$$lang.json not found"; \
			fi; \
		done; \
	fi

# Theme compilation: JSON → 3 binaries (colors_<name>.bin, fonts_<name>.bin, styles_<name>.bin)
# The default theme (specter) is ALWAYS compiled; extra themes are opt-in via ADD_THEME.
build-themes:
	@echo Building theme files...
	@mkdir -p build/flash_image/themes
	cd scenarios/MockUI/src/MockUI/basic/theming && python3 theme_compiler.py compile themes/specter_ui_theme_specter.json ../../../../../../build/flash_image/themes/
	@if [ -n "$(ADD_THEME)" ]; then \
		for theme in $(shell echo $(ADD_THEME) | tr ',' ' '); do \
			if [ -f scenarios/MockUI/src/MockUI/basic/theming/themes/specter_ui_theme_$$theme.json ]; then \
				echo "  Compiling $$theme..."; \
				cd scenarios/MockUI/src/MockUI/basic/theming && python3 theme_compiler.py compile themes/specter_ui_theme_$$theme.json ../../../../../../build/flash_image/themes/ || true; \
			else \
				echo "  Warning: theme file scenarios/MockUI/src/MockUI/basic/theming/themes/specter_ui_theme_$$theme.json not found"; \
			fi; \
		done; \
	fi

# Create FAT12 filesystem image with language files
# Uses tools/make_fat_image.py (pure Python, no extra dependencies).
# Matches MicroPython oofatfs f_mkfs(FM_FAT) output for STM32F469:
#   512-byte sectors, 192 sectors (96KB), 1 FAT, 512 root entries, label "pybflash"
build-flash-image: build-i18n build-themes
	@echo Creating FAT12 filesystem image...
	@echo "  Files to include:"
	@ls -lh build/flash_image/i18n/
	@ls -lh build/flash_image/themes/
	python3 tools/make_fat_image.py --source build/flash_image --output build/flash_fs.img
	@echo "✓ Filesystem image created: build/flash_fs.img"
	@ls -lh build/flash_fs.img

# cross-compiler
mpy-cross: $(TARGET_DIR) $(MPY_DIR)/mpy-cross/Makefile
	@echo Building cross-compiler
	make -C $(MPY_DIR)/mpy-cross \
	DEBUG=$(DEBUG) && \
	cp $(MPY_DIR)/mpy-cross/build/mpy-cross $(TARGET_DIR)

# disco board with bitcoin library
playground: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		FLAVOR=$(FLAVOR) \
		USE_DBOOT=$(USE_DBOOT) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_PLAYGROUND) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.elf \
		$(TARGET_DIR)/specter-diy.bin && \
	cp $(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.hex \
		$(TARGET_DIR)/specter-diy.hex

# disco board with bitcoin library
disco: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		FLAVOR=$(FLAVOR) \
		USE_DBOOT=$(USE_DBOOT) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_DISCO) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.elf \
		$(TARGET_DIR)/specter-diy.bin && \
	cp $(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.hex \
		$(TARGET_DIR)/specter-diy.hex

# disco board with bitcoin library
debug: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		FLAVOR=$(FLAVOR) \
		USE_DBOOT=$(USE_DBOOT) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_DEBUG) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.elf \
		$(TARGET_DIR)/debug.bin && \
	cp $(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.hex \
		$(TARGET_DIR)/debug.hex


# hello world scenario
hello: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/stm32
	@echo Building hello world firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		FLAVOR=$(FLAVOR) \
		USE_DBOOT=$(USE_DBOOT) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_HELLO) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.elf \
		$(TARGET_DIR)/hello.bin && \
	cp $(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.hex \
		$(TARGET_DIR)/hello.hex

# MockUI firmware with embedded filesystem
mockui: $(TARGET_DIR) mpy-cross trim-icons build-i18n build-flash-image $(MPY_DIR)/ports/stm32
	@echo Building MockUI firmware
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		FLAVOR=$(FLAVOR) \
		USE_DBOOT=$(USE_DBOOT) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_MOCKUI) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' \
		DEBUG=$(DEBUG) && \
	arm-none-eabi-objcopy -O binary \
		$(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.elf \
		$(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.bin
	@echo Merging firmware with filesystem image...
	python3 tools/merge_firmware_flash.py \
		--firmware $(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.bin \
		--filesystem build/flash_fs.img \
		--output $(TARGET_DIR)/mockui.bin
	@echo "✓ MockUI firmware with embedded filesystem: $(TARGET_DIR)/mockui.bin"
	@ls -lh $(TARGET_DIR)/mockui.bin

# unixport (simulator)
unix: $(TARGET_DIR) mpy-cross build-i18n build-themes $(MPY_DIR)/ports/unix
	@echo Building binary with frozen files
	make -C $(MPY_DIR)/ports/unix \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_UNIX) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' && \
	cp $(MPY_DIR)/ports/unix/build-standard/micropython $(TARGET_DIR)/micropython_unix

SCRIPT ?= mockui_fw/main.py

simulate: unix
	$(TARGET_DIR)/micropython_unix scenarios/$(SCRIPT)

all: mpy-cross disco unix

clean:
	rm -rf $(TARGET_DIR)
	rm -rf build
	rm -f scenarios/MockUI/src/MockUI/basic/i18n/translation_keys.py scenarios/MockUI/src/MockUI/basic/i18n/language_config.json
	make -C $(MPY_DIR)/mpy-cross clean
	rm -rf $(MPY_DIR)/mpy-cross/build
	make -C $(MPY_DIR)/ports/unix \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_UNIX) clean
	make -C $(MPY_DIR)/ports/stm32 \
		BOARD=$(BOARD) \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_DISCO) clean

# RAG code scanner
rag-setup:
	cd .rag && python -m venv .venv && .venv/bin/pip install -r requirements.txt

rag-index:
	cd .rag && .venv/bin/python indexer.py --rebuild

rag-search:
	cd .rag && .venv/bin/python search.py "$(QUERY)"

.PHONY: all clean sync-i18n build-i18n build-themes rag-setup rag-index rag-search

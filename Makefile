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

# Validate ADD_LANG to prevent shell injection (only lowercase letters and commas allowed)
ifneq ($(ADD_LANG),)
ifneq ($(shell echo "$(ADD_LANG)" | grep -E '^[a-z,]+$$'),$(ADD_LANG))
$(error ADD_LANG contains invalid characters. Use only lowercase letters and commas, e.g. ADD_LANG=de,fr)
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

# i18n compilation
build-i18n: sync-i18n
	@echo Building i18n files...
	@mkdir -p build/flash_image/i18n
	@cd scenarios/MockUI/src/MockUI/i18n && python3 lang_compiler.py generate_keys languages/specter_ui_en.json
	@cd scenarios/MockUI/src/MockUI/i18n && python3 lang_compiler.py compile languages/specter_ui_en.json && mv lang_en.bin ../../../../../build/flash_image/i18n/
	@if [ -n "$(ADD_LANG)" ]; then \
		for lang in $(shell echo $(ADD_LANG) | tr ',' ' '); do \
			if [ -f scenarios/MockUI/src/MockUI/i18n/languages/specter_ui_$$lang.json ]; then \
				echo "  Compiling $$lang..."; \
				cd scenarios/MockUI/src/MockUI/i18n && python3 lang_compiler.py compile languages/specter_ui_$$lang.json && mv lang_$$lang.bin ../../../../../build/flash_image/i18n/ || true; \
			else \
				echo "  Warning: Language file languages/specter_ui_$$lang.json not found"; \
			fi; \
		done; \
	fi

# Create FAT12 filesystem image with language files
# Uses tools/make_fat_image.py (pure Python, no extra dependencies).
# Matches MicroPython oofatfs f_mkfs(FM_FAT) output for STM32F469:
#   512-byte sectors, 192 sectors (96KB), 1 FAT, 512 root entries, label "pybflash"
build-flash-image: build-i18n
	@echo Creating FAT12 filesystem image...
	@echo "  Files to include:"
	@ls -lh build/flash_image/i18n/
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
mockui: $(TARGET_DIR) mpy-cross build-i18n build-flash-image $(MPY_DIR)/ports/stm32
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
unix: $(TARGET_DIR) mpy-cross $(MPY_DIR)/ports/unix
	@echo Building binary with frozen files
	make -C $(MPY_DIR)/ports/unix \
		USER_C_MODULES=$(USER_C_MODULES) \
		FROZEN_MANIFEST=$(FROZEN_MANIFEST_UNIX) \
		CFLAGS_EXTRA='-DMP_CONFIGFILE="<mpconfigport_specter.h>"' && \
	cp $(MPY_DIR)/ports/unix/build-standard/micropython $(TARGET_DIR)/micropython_unix

SCRIPT ?= mock_ui.py

simulate: unix
	$(TARGET_DIR)/micropython_unix scenarios/$(SCRIPT)

all: mpy-cross disco unix

clean:
	rm -rf $(TARGET_DIR)
	rm -rf build
	rm -f scenarios/MockUI/src/MockUI/i18n/translation_keys.py scenarios/MockUI/src/MockUI/i18n/language_config.json
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

.PHONY: all clean sync-i18n build-i18n rag-setup rag-index rag-search

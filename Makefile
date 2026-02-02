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

$(TARGET_DIR):
	mkdir -p $(TARGET_DIR)

# check submodules
$(MPY_DIR)/mpy-cross/Makefile:
	git submodule update --init --recursive

# i18n compilation
build-i18n:
	@echo Building i18n files...
	@mkdir -p src/data/lang
	@cd scenarios/MockUI/i18n && python3 lang_compiler.py generate_keys specter_ui_en.json
	@cd scenarios/MockUI/i18n && python3 lang_compiler.py compile specter_ui_en.json && mv lang_en.bin ../../../src/data/lang/
	@if [ -n "$(ADD_LANG)" ]; then \
		for lang in $(shell echo $(ADD_LANG) | tr ',' ' '); do \
			if [ -f scenarios/MockUI/i18n/specter_ui_$$lang.json ]; then \
				echo "  Compiling $$lang..."; \
				cd scenarios/MockUI/i18n && python3 lang_compiler.py compile specter_ui_$$lang.json && mv lang_$$lang.bin ../../../src/data/lang/ || true; \
			else \
				echo "  Warning: Language file specter_ui_$$lang.json not found"; \
			fi; \
		done; \
	fi

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

# MockUI firmware
mockui: $(TARGET_DIR) mpy-cross build-i18n $(MPY_DIR)/ports/stm32
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
		$(TARGET_DIR)/mockui.bin && \
	cp $(MPY_DIR)/ports/stm32/build-STM32F469DISC/firmware.hex \
		$(TARGET_DIR)/mockui.hex

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
	rm -f scenarios/MockUI/i18n/translation_keys.py scenarios/MockUI/i18n/language_config.json
	rm -rf src/data
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

.PHONY: all clean build-i18n rag-setup rag-index rag-search

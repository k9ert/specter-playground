# MockUI firmware manifest
# Include display wrapper and common libs
include('../f469-disco/manifests/disco.py')
# platform.py and config_default.py needed for SDRAM init
freeze('../src', ('platform.py', 'config_default.py'))
# MockUI package — only src/ is frozen; tests/ stay out of firmware.
freeze('../scenarios/MockUI/src')
# Other scenario modules
freeze('../scenarios', ('address_navigator.py', 'udisplay_demo.py'))
freeze('../scenarios/sim_control')
# boot.py and main.py entry points (frozen at root level)
freeze('../scenarios/mockui_fw')

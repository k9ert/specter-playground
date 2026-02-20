# MockUI firmware manifest
# Include display wrapper and common libs
include('../f469-disco/manifests/disco.py')
# platform.py and config_default.py needed for SDRAM init
freeze('../src', ('platform.py', 'config_default.py'))
# MockUI package (and other scenarios)
freeze('../scenarios')
# boot.py and main.py entry points (frozen at root level)
freeze('../scenarios/mockui_fw')

include('../f469-disco/manifests/disco.py')
# MockUI package — only src/ is frozen; tests/ stay out of firmware.
freeze('../scenarios/MockUI/src')
# Other scenario modules (mockui_fw excluded: its boot.py would conflict with boot/main)
freeze('../scenarios', ('address_navigator.py', 'udisplay_demo.py'))
freeze('../scenarios/sim_control')
freeze('../boot/main')

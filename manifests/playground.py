include('../f469-disco/manifests/disco.py')
# MockUI package — only src/ is frozen; tests/ stay out of firmware.
freeze('../scenarios/MockUI/src')
freeze('../scenarios', ('address_navigator.py', 'udisplay_demo.py'))
freeze('../scenarios/sim_control')
freeze('../scenarios/hello_world')
freeze('../boot/main')

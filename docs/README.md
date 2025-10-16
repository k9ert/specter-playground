# Documentation

Set this up as explained in the original project: 
https://github.com/cryptoadvance/specter-diy/blob/master/docs/build.md

For now, this is mainly targeting for simulation. `make disco` might not work yet.

There is some video documentation coming up soon.

Different scenarios can be simulated like:

```
# Default - runs mock_structure.py
nix develop -c make simulate SCRIPT=mock_structure.py

# Run address_navigator
nix develop -c make simulate SCRIPT=address_navigator.py

# Run udisplay_demo
nix develop -c make simulate SCRIPT=udisplay_demo.py
```

Feel free to contribute! I'll probably merge your PRs without (much) review.

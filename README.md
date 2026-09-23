# Specter-Playground

    "Cypherpunks write code. We know that someone has to write software to defend privacy, 
    and since we can't get privacy unless we all do, we're going to write it."
    A Cypherpunk's Manifesto - Eric Hughes - 9 March 1993

    ...and Cypherpunks do build their own Bitcoin Hardware Wallets.

![](https://raw.githubusercontent.com/cryptoadvance/specter-diy/master/docs/pictures/kit.jpg)

The idea of the project is to provide a playground for everyone to play with a software which can potentially run on the Specter Hardware, a F469-Discovery board from STMicroelectronics.

## setup
```
git clone --recurse-submodules https://github.com/k9ert/specter-playground.git
cd specter-playground
# install nix + direnv, then:
direnv allow
make simulate            # build and run the MockUI simulator
```

If you cloned without `--recurse-submodules`, run `git submodule update --init --recursive`.

Unit tests (`make test` runs the i18n build first, which generates `translation_keys.py`):

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
make test
```

Shared simulator and hardware control lives in the [`devtools/`](devtools) submodule ([specter-devtools](https://github.com/maggo83/specter-devtools)); see [CLAUDE.md](CLAUDE.md) for its setup and `make simulate-automation`.

## Scenarios

Different UI scenarios can be tested using the `SCRIPT` parameter:

```bash
# Default - runs the MockUI (scenarios/mockui_fw/main.py)
nix develop -c make simulate

# Run address_navigator scenario
nix develop -c make simulate SCRIPT=address_navigator.py

# Run udisplay_demo scenario
nix develop -c make simulate SCRIPT=udisplay_demo.py
```

### MockUI
![](./docs/MockUI/screens/main/screenshot.png)

### Address Navigator
![](./docs/address_simulator.png)

### UDisplay Demo
![](./docs/udisplay_demo.png)

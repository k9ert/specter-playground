# Project Context

## Codebase Overview

| Directory | Description |
|-----------|-------------|
| `scenarios/` | **New MockUI** - clickable prototype, no real functionality yet |
| `specter-diy-src/` | **Old specter-diy** (symlink) - working code, ugly UI, reference implementation |
| `f469-disco/` | MicroPython + LVGL build system, C modules. Temporarily pinned to `maggo83/f469-disco_disco_tool` branch `fix/sdl-screenshot-rgba32` (SDL screenshot + color fix) until [miketlk/f469-disco#1](https://github.com/miketlk/f469-disco/pull/1) and its follow-up [#3](https://github.com/miketlk/f469-disco/pull/3) are merged |
| `devtools/` | [specter-devtools](https://github.com/maggo83/specter-devtools) submodule: shared simulator/hardware control, F469 `disco` tool, simulator control runtime |

## Simulator and Hardware Control

Use `specter-devtools` from the `devtools/` submodule. It sends the same JSON
request to the simulator or an attached board; only `--target` changes.

```bash
# One-time setup
python3 -m venv devtools/.venv
devtools/.venv/bin/pip install -r devtools/f469/requirements.txt -e devtools

# Build and start the simulator with its control server
make simulate-automation

# In another terminal
source devtools/.venv/bin/activate
specter-devtools --target simulator request '{"action":"capabilities"}'  # test connection
specter-devtools --target simulator state                  # current menu + device state
specter-devtools --target simulator click "Manage Device"  # click by visible text
specter-devtools --target simulator goto manage_security   # open a menu by id
specter-devtools --target simulator back                   # go back
specter-devtools --target simulator labels                 # visible texts
specter-devtools --target simulator set is_locked false    # modify device state
specter-devtools --target simulator capture /tmp/screen    # screenshot + labels + tree
specter-devtools --target simulator explore docs/MockUI/screens  # capture every menu

# Attached F469 board running MockUI firmware
specter-devtools --target f469 click "Manage Device"
specter-devtools --target f469 screenshot /tmp/board.png
specter-devtools --target f469 board flash program bin/mockui.bin
```

`click`, `tree`, `labels`, `screenshot`, and `capture` work on both targets;
`state`, `goto`, `back`, `set`, and `explore` need application state, which only
the simulator offers. To restart the simulator, stop it and run
`make simulate-automation` again.

The simulator serves NDJSON on TCP port 9876, e.g.
`echo '{"action":"control","request":{"action":"tree"}}' | nc 127.0.0.1 9876`.
See `devtools/docs/control-contract.md` for actions, response formats, and
target differences.

Troubleshooting: *connection refused* means the simulator isn't running or
crashed; *EADDRINUSE* means a stale process still holds port 9876
(`lsof -ti:9876 | xargs kill`); for *widget not found*, check the exact text
with `labels` (and `labels --layer top` for overlays).

## UI Validation

If correctness is important, for every state-changing UI input on the simulator
or attached hardware, capture a framebuffer screenshot immediately afterward
and treat it as the source of truth for the visible result. Widget trees and
command responses are useful diagnostics but do not prove that a control is
visible, enabled, or that a transition completed. Inspect the `top` layer
for overlays before interacting with the screen beneath it.

## RAG Code Search

MCP tool `search_codebase` available. Indexes both repos.

```bash
# Re-index after code changes
make rag-index
```

## Key Points

- MockUI in `scenarios/` is the **target design** - modern, clean
- Old code in `specter-diy-src/` has **working logic** to reference
- Goal: port functionality from old to new UI

See `docs/rag-setup.md` for setup.

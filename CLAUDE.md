# Project Context

## Codebase Overview

| Directory | Description |
|-----------|-------------|
| `scenarios/` | **New MockUI** - clickable prototype, no real functionality yet |
| `specter-diy-src/` | **Old specter-diy** (symlink) - working code, ugly UI, reference implementation |
| `f469-disco/` | MicroPython + LVGL build system, C modules. Temporarily pinned to `maggo83/f469-disco_disco_tool` branch `fix/sdl-screenshot-rgba32` (SDL screenshot + color fix) until [miketlk/f469-disco#1](https://github.com/miketlk/f469-disco/pull/1) and its follow-up [#3](https://github.com/miketlk/f469-disco/pull/3) are merged |
| `devtools/` | [specter-devtools](https://github.com/maggo83/specter-devtools) submodule: shared simulator/hardware control, F469 `disco` tool, simulator control runtime |
| `mcp-servers/lvgl-sim/` | MCP server + CLI for simulator control |

## Simulator Control

### Quick Start
```bash
# Build and start simulator with control server
make simulate-automation

# Test with CLI (in another terminal)
cd mcp-servers/lvgl-sim
.venv/bin/python sim_cli.py ping
.venv/bin/python sim_cli.py screenshot /tmp/screenshot.png
```

You can also use the MCP server directly but some common scanrios and
helpers are in the sim_cli.py.

### sim_cli.py Commands
```
Usage: sim_cli.py [OPTIONS] COMMAND [ARGS]...

Commands:
  back        Navigate back to previous menu.
  capture     Capture screenshot, labels, and tree to a folder.
  click       Click a button by its text label.
  goto        Navigate directly to a menu by ID.
  labels      List visible text labels.
  ping        Test connection to simulator.
  restart     Restart the simulator process.
  screenshot  Capture screenshot to PNG file.
  set         Set a state attribute (e.g., seed_loaded, is_locked).
  state       Show current UI state.
  tree        Dump full widget tree as JSON.
```

Examples:
```bash
sim_cli.py ping                     # test connection
sim_cli.py state                    # show current menu + state
sim_cli.py click "Manage Device"    # click button
sim_cli.py goto manage_security     # navigate directly to menu
sim_cli.py back                     # go back
sim_cli.py capture /tmp/screen      # save screenshot + labels + tree
sim_cli.py set seed_loaded true     # modify state
sim_cli.py restart                  # restart simulator
```

### Protocol (TCP:9876)
```bash
echo '{"action":"ping"}' | nc 127.0.0.1 9876
echo '{"action":"screenshot"}' | nc 127.0.0.1 9876
echo '{"action":"click","text":"Manage Device"}' | nc 127.0.0.1 9876
```

See `docs/lvgl-sim-mcp.md` for full documentation.

## Shared Simulator and Hardware Control

Use `specter-devtools` from the `devtools/` submodule for portable UI checks. It
sends the same JSON request to the simulator or an attached board; only
`--target` changes. Application state and navigation requests are simulator-only.

```bash
# One-time setup
python3 -m venv devtools/.venv
devtools/.venv/bin/pip install -r devtools/f469/requirements.txt -e devtools

# Simulator (started with make simulate-automation)
devtools/.venv/bin/specter-devtools --target simulator request '{"action":"tree"}'

# Attached F469 board running MockUI firmware
devtools/.venv/bin/specter-devtools --target f469 request '{"action":"tree"}'
devtools/.venv/bin/specter-devtools --target f469 board flash program bin/mockui.bin
```

See `devtools/docs/control-contract.md` for actions, response formats, and
target differences.

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

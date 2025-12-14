# Project Context

## Codebase Overview

| Directory | Description |
|-----------|-------------|
| `scenarios/` | **New MockUI** - clickable prototype, no real functionality yet |
| `specter-diy-src/` | **Old specter-diy** (symlink) - working code, ugly UI, reference implementation |
| `f469-disco/` | MicroPython + LVGL build system, C modules |
| `mcp-servers/lvgl-sim/` | MCP server + CLI for simulator control |

## Simulator Control

### Quick Start
```bash
# Start simulator with control server
bin/micropython_unix scenarios/mock_ui.py --control

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

## RAG Code Search

MCP tool `search_codebase` available. Indexes both repos.

```bash
# Re-index after code changes
make rag-index
```

See `docs/rag-setup.md` for setup.

## Key Points

- MockUI in `scenarios/` is the **target design** - modern, clean
- Old code in `specter-diy-src/` has **working logic** to reference
- Goal: port functionality from old to new UI

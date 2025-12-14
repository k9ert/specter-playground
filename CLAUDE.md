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

### sim_cli.py Commands
- `ping` - test connection
- `state` - show SpecterState + UIState
- `labels` - list visible button labels
- `click "Button Text"` - click a button
- `set attr value` - modify state (e.g. `set seed_loaded true`)
- `screenshot /path/to/file.png` - capture PNG screenshot
- `tree` - dump full widget tree JSON

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

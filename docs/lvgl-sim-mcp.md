# LVGL Simulator MCP Server

MCP server for controlling the LVGL simulator, enabling automated UI testing via Claude Code.

## Architecture

```
Claude ─── MCP (stdio) ─── MCP Server ─── TCP:9876 ─── Simulator
                          (Python 3)                   (MicroPython)
```

- **MCP Server** (`mcp-servers/lvgl-sim/`) - Python 3 process, spawns simulator
- **Control Server** (`scenarios/sim_control/`) - Runs inside simulator, handles commands

## Setup

```bash
# Create venv (already done if following setup)
cd mcp-servers/lvgl-sim
python3 -m venv .venv
.venv/bin/pip install 'mcp>=1.0.0'
```

MCP config in `.mcp.json`:
```json
{
  "mcpServers": {
    "lvgl-sim": {
      "command": "/path/to/specter-playground/mcp-servers/lvgl-sim/.venv/bin/python",
      "args": ["/path/to/specter-playground/mcp-servers/lvgl-sim/mcp_server.py"]
    }
  }
}
```

Restart Claude Code to load the MCP server.

## Tools

| Tool | Description |
|------|-------------|
| `start_simulator` | Spawn simulator, connect to control socket |
| `stop_simulator` | Kill simulator process |
| `get_widget_tree` | Dump full widget tree as JSON |
| `find_widget` | Find widget by text label |
| `click_widget` | Click widget by text label |
| `get_state` | Get SpecterState + UIState |
| `set_state` | Modify SpecterState attribute |
| `screenshot` | Capture screenshot, returns file path |

## Usage Examples

### Start simulator and click a button
```
1. start_simulator
2. click_widget(text="Manage Device")
3. get_state  # verify navigation
```

### Inspect UI state
```
get_state
→ {
    "specter": {"seed_loaded": false, "is_locked": false, ...},
    "ui": {"current_menu_id": "main", "history": [], "modal": null}
  }
```

### Navigate and verify
```
click_widget(text="Manage Device")
get_state
→ ui.current_menu_id = "manage_device"
→ ui.history = ["main"]
```

## Screenshot

The screenshot command writes raw RGB565 data directly to `/tmp/sim_screenshot.raw`, bypassing MicroPython's heap to avoid memory allocation failures.

```
screenshot
→ {"ok": true, "width": 480, "height": 800, "format": "RGB565", "file": "/tmp/sim_screenshot.raw"}
```

The raw file can be converted to PNG using PIL (see sim_cli.py for implementation).

### Technical Details

Screenshots use `SDL_RenderReadPixels` in 32-row chunks to minimize memory:
- C code reads RGBA from SDL renderer
- Converts to RGB565 (2 bytes/pixel vs 4)
- Writes directly to file via stdio
- Never allocates large buffers in Python heap

This solves the MicroPython memory limitation where `mp_obj_new_bytes` cannot allocate 768KB+ contiguous memory due to heap fragmentation.

## CLI Tool (sim_cli.py)

`mcp-servers/lvgl-sim/sim_cli.py` provides a command-line interface for manual testing:

```bash
cd mcp-servers/lvgl-sim

# Basic commands
.venv/bin/python sim_cli.py ping          # Test connection
.venv/bin/python sim_cli.py state         # Show current state
.venv/bin/python sim_cli.py labels        # List visible labels

# Navigation
.venv/bin/python sim_cli.py click "Manage Device"

# State manipulation
.venv/bin/python sim_cli.py set seed_loaded true

# Screenshot (converts to PNG)
.venv/bin/python sim_cli.py screenshot /tmp/screenshot.png

# Full widget tree
.venv/bin/python sim_cli.py tree
```

## Manual Testing

Run simulator with control mode:
```bash
bin/micropython_unix scenarios/mock_ui.py --control
```

Test via netcat:
```bash
echo '{"action":"ping"}' | nc 127.0.0.1 9876
# → {"ok": true, "pong": true}

echo '{"action":"get_state"}' | nc 127.0.0.1 9876
# → {"ok": true, "specter": {...}, "ui": {...}}

echo '{"action":"screenshot"}' | nc 127.0.0.1 9876
# → {"ok": true, "width": 480, "height": 800, "file": "/tmp/sim_screenshot.raw"}
```

## Protocol

NDJSON over TCP port 9876.

**Requests:**
```json
{"action": "ping"}
{"action": "widget_tree"}
{"action": "click", "text": "Button Label"}
{"action": "get_state"}
{"action": "set_state", "attr": "is_locked", "value": true}
```

**Responses:**
```json
{"ok": true, ...}
{"ok": false, "error": "Error message"}
```

## Widget Tree

Buttons contain label children. To click a button, search for its label text:

```json
{
  "type": "button",
  "x": 10, "y": 100,
  "children": [
    {"type": "label", "text": "Manage Device", ...}
  ]
}
```

`click_widget(text="Manage Device")` finds the label, then clicks its parent button.

## Troubleshooting

**Connection refused**: Simulator not running or crashed. Check `bin/micropython_unix` process.

**EADDRINUSE**: Port 9876 still bound. Kill stale processes: `lsof -ti:9876 | xargs kill`

**Widget not found**: Check exact button text via `get_widget_tree` or screenshot.

**Referenced object deleted**: Expected after click - old screen widgets are destroyed when navigating.

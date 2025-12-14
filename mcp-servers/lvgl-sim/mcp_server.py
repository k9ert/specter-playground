#!/usr/bin/env python3
"""MCP server for LVGL simulator control."""
import asyncio
import json
import socket
import subprocess
import sys
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
SIMULATOR_BIN = PROJECT_ROOT / "bin" / "micropython_unix"
SIMULATOR_SCRIPT = PROJECT_ROOT / "scenarios" / "mock_ui.py"
CONTROL_PORT = 9876


server = Server("lvgl-sim")

# Global state
sim_process = None
sim_socket = None


def connect_to_simulator(timeout_ms=5000):
    """Connect to simulator control socket with retry."""
    global sim_socket

    deadline = asyncio.get_event_loop().time() + (timeout_ms / 1000)

    while asyncio.get_event_loop().time() < deadline:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(("127.0.0.1", CONTROL_PORT))
            sim_socket = sock
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            import time
            time.sleep(0.1)

    return False


def send_command(cmd):
    """Send command to simulator and get response."""
    global sim_socket

    if not sim_socket:
        return {"ok": False, "error": "Not connected to simulator"}

    try:
        data = json.dumps(cmd) + "\n"
        sim_socket.sendall(data.encode())

        # Read response (newline-delimited)
        buf = b""
        sim_socket.settimeout(5.0)
        while b"\n" not in buf:
            chunk = sim_socket.recv(65536)
            if not chunk:
                return {"ok": False, "error": "Connection closed"}
            buf += chunk

        line = buf.split(b"\n")[0]
        return json.loads(line.decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}


@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="start_simulator",
            description="Start the LVGL simulator and connect to control socket",
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_ms": {
                        "type": "integer",
                        "description": "Connection timeout in ms",
                        "default": 5000,
                    },
                },
            },
        ),
        Tool(
            name="stop_simulator",
            description="Stop the LVGL simulator",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_widget_tree",
            description="Get the full widget tree of current screen",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="find_widget",
            description="Find widget by text label",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to search for in widget labels",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="click_widget",
            description="Click a widget identified by its text label",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text label of widget to click",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="get_state",
            description="Get current SpecterState and UIState",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="set_state",
            description="Set an attribute on SpecterState",
            inputSchema={
                "type": "object",
                "properties": {
                    "attr": {
                        "type": "string",
                        "description": "Attribute name to set",
                    },
                    "value": {
                        "description": "Value to set",
                    },
                },
                "required": ["attr", "value"],
            },
        ),
        Tool(
            name="screenshot",
            description="Capture screenshot of current simulator state and save as PNG",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Output filename (default: /tmp/sim_screenshot.png)",
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    global sim_process, sim_socket

    if name == "start_simulator":
        timeout_ms = arguments.get("timeout_ms", 5000)

        if sim_process and sim_process.poll() is None:
            return [TextContent(type="text", text="Simulator already running")]

        # Start simulator with --control flag
        try:
            sim_process = subprocess.Popen(
                [str(SIMULATOR_BIN), str(SIMULATOR_SCRIPT), "--control"],
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            return [TextContent(type="text", text=f"Failed to start simulator: {e}")]

        # Connect to control socket
        if connect_to_simulator(timeout_ms):
            # Verify connection with ping
            resp = send_command({"action": "ping"})
            if resp.get("ok"):
                return [TextContent(type="text", text="Simulator started and connected")]
            return [TextContent(type="text", text=f"Connected but ping failed: {resp}")]

        sim_process.kill()
        sim_process = None
        return [TextContent(type="text", text="Failed to connect to simulator control socket")]

    elif name == "stop_simulator":
        if sim_socket:
            try:
                sim_socket.close()
            except:
                pass
            sim_socket = None

        if sim_process:
            sim_process.terminate()
            try:
                sim_process.wait(timeout=2)
            except:
                sim_process.kill()
            sim_process = None
            return [TextContent(type="text", text="Simulator stopped")]

        return [TextContent(type="text", text="Simulator was not running")]

    elif name == "get_widget_tree":
        resp = send_command({"action": "widget_tree"})
        return [TextContent(type="text", text=json.dumps(resp, indent=2))]

    elif name == "find_widget":
        text = arguments.get("text", "")
        # Get tree and search client-side
        resp = send_command({"action": "widget_tree"})
        if not resp.get("ok"):
            return [TextContent(type="text", text=json.dumps(resp))]

        def search(node, target):
            if node.get("text") == target:
                return node
            for child in node.get("children", []):
                result = search(child, target)
                if result:
                    return result
            return None

        found = search(resp["tree"], text)
        if found:
            return [TextContent(type="text", text=json.dumps({"ok": True, "widget": found}, indent=2))]
        return [TextContent(type="text", text=json.dumps({"ok": False, "error": f"Widget with text '{text}' not found"}))]

    elif name == "click_widget":
        text = arguments.get("text", "")
        resp = send_command({"action": "click", "text": text})
        return [TextContent(type="text", text=json.dumps(resp, indent=2))]

    elif name == "get_state":
        resp = send_command({"action": "get_state"})
        return [TextContent(type="text", text=json.dumps(resp, indent=2))]

    elif name == "set_state":
        attr = arguments.get("attr")
        value = arguments.get("value")
        resp = send_command({"action": "set_state", "attr": attr, "value": value})
        return [TextContent(type="text", text=json.dumps(resp, indent=2))]

    elif name == "screenshot":
        import time

        filename = arguments.get("filename", "/tmp/sim_screenshot.png")

        # Use macOS screencapture to capture the LVGL window
        # Find window by title "LVGL"
        try:
            # Get window list and find LVGL window
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get name of every window of every process'],
                capture_output=True, text=True, timeout=5
            )

            # Use screencapture with window selection
            # -l flag requires window ID, -w for interactive window select
            # For automation, we'll capture by window title using -l
            result = subprocess.run(
                ["osascript", "-e",
                 '''tell application "System Events"
                    set lvglWindow to first window of (first process whose name contains "micropython")
                    set winID to id of lvglWindow
                    return winID
                 end tell'''],
                capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                window_id = result.stdout.strip()
                subprocess.run(
                    ["screencapture", "-l", window_id, "-x", filename],
                    timeout=5
                )
                return [TextContent(type="text", text=f"Screenshot saved to {filename}")]

            # Fallback: capture by clicking on LVGL window area
            # Just capture entire screen region where simulator usually is
            subprocess.run(
                ["screencapture", "-R", "0,0,500,850", "-x", filename],
                timeout=5
            )
            return [TextContent(type="text", text=f"Screenshot saved to {filename} (region capture)")]

        except Exception as e:
            return [TextContent(type="text", text=f"Screenshot failed: {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

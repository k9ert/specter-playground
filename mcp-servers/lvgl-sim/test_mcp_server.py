import asyncio
import json
from unittest.mock import patch

import mcp_server


def run_tool(name, arguments):
    return asyncio.run(mcp_server.call_tool(name, arguments))


def test_control_request_forwards_the_canonical_request():
    request = {"action": "click", "text": "Manage Device"}
    with patch.object(mcp_server, "send_command", return_value={"ok": True}) as send:
        response = run_tool("control_request", {"request": request})

    assert json.loads(response[0].text) == {"ok": True}
    send.assert_called_once_with({"action": "control", "request": request})


def test_screenshot_uses_the_simulator_framebuffer_not_host_window_capture(tmp_path):
    raw_file = tmp_path / "screen.raw"
    raw_file.write_bytes(b"rgb565")
    output = tmp_path / "screen.png"
    screenshot = {"ok": True, "file": str(raw_file), "width": 2, "height": 1}

    with patch.object(mcp_server, "send_command", return_value=screenshot) as send, \
         patch.object(mcp_server, "save_rgb565_png") as save:
        response = run_tool("screenshot", {"filename": str(output)})

    assert json.loads(response[0].text) == {
        "ok": True,
        "file": str(output),
        "width": 2,
        "height": 1,
        "format": "PNG",
    }
    send.assert_called_once_with({"action": "screenshot"})
    save.assert_called_once_with(b"rgb565", str(output), 2, 1)
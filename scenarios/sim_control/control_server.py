"""TCP control server for simulator - runs inside MicroPython."""
import socket
import json
import lvgl as lv

from .widget_tree import get_widget_tree, find_widget_by_text


class ControlServer:
    """Non-blocking TCP server for remote control of simulator."""

    def __init__(self, nav_controller, port=9876):
        self.nav = nav_controller
        self.port = port
        self.socket = socket.socket()
        ai = socket.getaddrinfo("127.0.0.1", port)
        addr = ai[0][-1]
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(addr)
        self.socket.listen(1)
        self.socket.setblocking(False)
        self.client = None
        self.buf = b""

        # Create LVGL timer to poll for commands
        self.timer = lv.timer_create(self._poll, 50, None)

    def _poll(self, timer):
        """Called by LVGL timer to check for commands."""
        self._check_connection()
        self._process_commands()

    def _check_connection(self):
        """Accept new connections or read from existing."""
        if self.client is not None:
            try:
                b = self.client.recv(4096)
                if len(b) == 0:
                    self.client.close()
                    self.client = None
                else:
                    self.buf += b
            except OSError as e:
                if "EAGAIN" not in str(e) and "ECONNRESET" not in str(e):
                    self.client.close()
                    self.client = None
        else:
            try:
                res = self.socket.accept()
                self.client = res[0]
                self.client.setblocking(False)
            except OSError as e:
                if "EAGAIN" not in str(e):
                    pass  # No connection waiting

    def _process_commands(self):
        """Process any complete commands in buffer."""
        while b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            try:
                cmd = json.loads(line.decode())
                response = self._handle_command(cmd)
            except Exception as e:
                response = {"ok": False, "error": str(e)}
            self._send_response(response)

    def _send_response(self, response):
        """Send JSON response to client."""
        if self.client:
            try:
                data = json.dumps(response) + "\n"
                self.client.send(data.encode())
            except:
                pass

    def _handle_command(self, cmd):
        """Route command to handler."""
        action = cmd.get("action")

        if action == "widget_tree":
            return self._cmd_widget_tree()
        elif action == "click":
            return self._cmd_click(cmd)
        elif action == "get_state":
            return self._cmd_get_state()
        elif action == "set_state":
            return self._cmd_set_state(cmd)
        elif action == "ping":
            return {"ok": True, "pong": True}
        elif action == "screenshot":
            return self._cmd_screenshot()
        elif action == "navigate":
            return self._cmd_navigate(cmd)
        else:
            return {"ok": False, "error": "Unknown action: " + str(action)}

    def _cmd_navigate(self, cmd):
        """Navigate to a menu or back."""
        target = cmd.get("target")
        if target == "back" or target is None:
            self.nav.show_menu(None)
            return {"ok": True, "navigated": "back"}
        else:
            self.nav.show_menu(target)
            return {"ok": True, "navigated": target}

    def _cmd_widget_tree(self):
        """Return full widget tree."""
        screen = lv.screen_active()
        tree = get_widget_tree(screen)
        return {"ok": True, "tree": tree}

    def _cmd_click(self, cmd):
        """Click widget by text or path."""
        text = cmd.get("text")
        if text:
            screen = lv.screen_active()
            widget, label = find_widget_by_text(screen, text)
            if not widget:
                return {"ok": False, "error": "Widget not found: " + text}

            # Send click event
            widget.send_event(lv.EVENT.CLICKED, None)

            info = {
                "type": type(widget).__name__,
                "x": widget.get_x(),
                "y": widget.get_y(),
            }
            if label and hasattr(label, "get_text"):
                try:
                    info["text"] = label.get_text()
                except:
                    pass
            return {"ok": True, "clicked": info}

        return {"ok": False, "error": "Must provide 'text' to identify widget"}

    def _cmd_get_state(self):
        """Return SpecterState and UIState."""
        ss = self.nav.specter_state
        us = self.nav.ui_state

        # Serialize SpecterState
        specter = {
            "seed_loaded": ss.seed_loaded,
            "is_locked": ss.is_locked,
            "pin": ss.pin,
            "active_wallet": None,
            "registered_wallets": [],
            "hasUSB": ss.hasUSB,
            "enabledUSB": ss.enabledUSB,
            "hasQR": ss.hasQR,
            "enabledQR": getattr(ss, "enabledQR", False),
            "hasSD": ss.hasSD,
            "enabledSD": getattr(ss, "enabledSD", False),
            "detectedSD": getattr(ss, "detectedSD", False),
            "hasSmartCard": getattr(ss, "hasSmartCard", False),
            "enabledSmartCard": getattr(ss, "enabledSmartCard", False),
            "detectedSmartCard": getattr(ss, "detectedSmartCard", False),
        }

        if ss.active_wallet:
            specter["active_wallet"] = {
                "name": ss.active_wallet.name,
                "xpub": ss.active_wallet.xpub,
                "isMultiSig": ss.active_wallet.isMultiSig,
                "net": ss.active_wallet.net,
            }

        for w in ss.registered_wallets:
            specter["registered_wallets"].append({
                "name": w.name,
                "xpub": w.xpub,
                "isMultiSig": w.isMultiSig,
                "net": w.net,
            })

        # Serialize UIState
        ui = {
            "current_menu_id": us.current_menu_id,
            "history": list(us.history),
            "modal": us.modal,
        }

        return {"ok": True, "specter": specter, "ui": ui}

    def _cmd_set_state(self, cmd):
        """Set attribute on SpecterState."""
        attr = cmd.get("attr")
        value = cmd.get("value")

        if not attr:
            return {"ok": False, "error": "Must provide 'attr'"}

        ss = self.nav.specter_state
        if not hasattr(ss, attr):
            return {"ok": False, "error": "Unknown attr: " + attr}

        setattr(ss, attr, value)
        return {"ok": True, "set": {attr: value}}

    def _cmd_screenshot(self):
        """Capture screenshot - writes to file, returns path for MCP to read."""
        try:
            import SDL
            # Write screenshot directly to file (bypasses Python heap)
            filename = "/tmp/sim_screenshot.raw"
            w, h, _ = SDL.screenshot(filename)

            return {"ok": True, "width": w, "height": h, "format": "RGB565", "file": filename}
        except Exception as e:
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

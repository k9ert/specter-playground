"""TCP control server for simulator - runs inside MicroPython."""
import socket
import json
import lvgl as lv

from .widget_tree import get_widget_tree, find_widget_by_text, find_widget_at


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
        elif action == "dropup":
            return self._cmd_dropup(cmd)
        else:
            return {"ok": False, "error": "Unknown action: " + str(action)}

    def _cmd_dropup(self, cmd):
        """Directly toggle / open / close a drop-up panel."""
        which = cmd.get("which", "seed")   # "seed" or "wallet"
        op = cmd.get("op", "toggle")        # "toggle", "open", "close"
        nav = self.nav
        dropup = getattr(nav, "_seed_dropup" if which == "seed" else "_wallet_dropup", None)
        if dropup is None:
            return {"ok": False, "error": "dropup not registered: " + which}
        try:
            if op == "open":
                dropup.open()
            elif op == "close":
                dropup.close()
            else:
                dropup.toggle()
            return {"ok": True, "op": op, "which": which, "is_open": dropup.is_open()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _cmd_navigate(self, cmd):
        """Navigate to a menu or back."""
        target = cmd.get("target")
        if target == "back" or target is None:
            self.nav.navigate_to(None)
            return {"ok": True, "navigated": "back"}
        else:
            self.nav.navigate_to(target)
            return {"ok": True, "navigated": target}

    def _cmd_widget_tree(self):
        """Return full widget tree (screen + layer_top)."""
        screen = lv.screen_active()
        tree = get_widget_tree(screen)
        # Also include layer_top (where modals/overlays live)
        try:
            disp = lv.display_get_default()
            top = disp.get_layer_top()
            if top.get_child_count() > 0:
                tree["layer_top"] = get_widget_tree(top)
        except:
            pass
        return {"ok": True, "tree": tree}

    def _cmd_click(self, cmd):
        """Click widget by text or screen coordinates."""
        text = cmd.get("text")
        x = cmd.get("x")
        y = cmd.get("y")

        if x is not None and y is not None:
            # Find deepest widget at coordinates by traversing widget tree
            screen = lv.screen_active()
            target = find_widget_at(screen, x, y)
            if target is None:
                return {"ok": False, "error": "No widget at ({}, {})".format(x, y)}
            # If the found widget is a non-clickable type (e.g. image/label), walk up to find a button
            obj = target
            while obj is not None:
                type_name = type(obj).__name__
                if type_name in ("button", "Button", "lv_button"):
                    break
                try:
                    parent = obj.get_parent()
                    if parent is None or parent == obj:
                        break
                    obj = parent
                except:
                    break
            obj.send_event(lv.EVENT.CLICKED, None)
            return {"ok": True, "clicked": {"x": x, "y": y, "type": type(obj).__name__}}

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

        return {"ok": False, "error": "Must provide 'text' or 'x'+'y' to identify widget"}

    def _cmd_get_state(self):
        """Return DeviceState and UIState."""
        ss = self.nav.device_state
        us = self.nav.ui_state

        # Serialize DeviceState — use getattr for forwards/backwards compat
        specter = {
            "seed_loaded": bool(getattr(ss, "loaded_seeds", [])),
            "loaded_seed_count": len(getattr(ss, "loaded_seeds", [])),
            "is_locked": getattr(ss, "is_locked", False),
            "pin": getattr(ss, "pin", None),
            "active_wallet": None,
            "registered_wallets": [],
            "hasUSB": ss.hasUSB() if callable(getattr(ss, "hasUSB", None)) else getattr(ss, "hasUSB", False),
            "enabledUSB": ss.USB_enabled() if callable(getattr(ss, "USB_enabled", None)) else getattr(ss, "enabledUSB", False),
            "hasQR": ss.hasQR() if callable(getattr(ss, "hasQR", None)) else getattr(ss, "hasQR", False),
            "enabledQR": ss.QR_enabled() if callable(getattr(ss, "QR_enabled", None)) else getattr(ss, "enabledQR", False),
            "hasSD": ss.hasSD() if callable(getattr(ss, "hasSD", None)) else getattr(ss, "hasSD", False),
            "enabledSD": ss.SD_enabled() if callable(getattr(ss, "SD_enabled", None)) else getattr(ss, "enabledSD", False),
            "detectedSD": ss.SD_detected() if callable(getattr(ss, "SD_detected", None)) else getattr(ss, "detectedSD", False),
            "hasSmartCard": ss.hasSmartCard() if callable(getattr(ss, "hasSmartCard", None)) else getattr(ss, "hasSmartCard", False),
            "enabledSmartCard": ss.SmartCard_enabled() if callable(getattr(ss, "SmartCard_enabled", None)) else getattr(ss, "enabledSmartCard", False),
            "detectedSmartCard": ss.SmartCard_detected() if callable(getattr(ss, "SmartCard_detected", None)) else getattr(ss, "detectedSmartCard", False),
        }

        if ss.active_wallet:
            specter["active_wallet"] = {
                "name": getattr(ss.active_wallet, "label", getattr(ss.active_wallet, "name", None)),
                "descriptor": getattr(ss.active_wallet, "descriptor", getattr(ss.active_wallet, "xpub", None)),
                "isMultiSig": getattr(ss.active_wallet, "isMultiSig", False),
                "net": getattr(ss.active_wallet, "net", "mainnet"),
            }

        for w in getattr(ss, "registered_wallets", []):
            specter["registered_wallets"].append({
                "name": getattr(w, "label", getattr(w, "name", None)),
                "descriptor": getattr(w, "descriptor", getattr(w, "xpub", None)),
                "isMultiSig": getattr(w, "isMultiSig", False),
                "net": getattr(w, "net", "mainnet"),
            })

        # Serialize UIState
        ui = {
            "current_menu_id": us.current_menu_id,
            "history": list(getattr(us, "history", [])),
            "modal": getattr(us, "modal", None),
        }

        return {"ok": True, "specter": specter, "ui": ui}

    def _cmd_set_state(self, cmd):
        """Set attribute on DeviceState."""
        attr = cmd.get("attr")
        value = cmd.get("value")

        if not attr:
            return {"ok": False, "error": "Must provide 'attr'"}

        ss = self.nav.device_state
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

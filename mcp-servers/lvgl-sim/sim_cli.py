#!/usr/bin/env python3
"""Simple CLI for simulator control. Usage:

    .venv/bin/python sim_cli.py ping
    .venv/bin/python sim_cli.py state
    .venv/bin/python sim_cli.py click "Manage Device"
    .venv/bin/python sim_cli.py labels
    .venv/bin/python sim_cli.py set seed_loaded true
    .venv/bin/python sim_cli.py screenshot [filename.png]
"""
import socket
import json
import sys
import base64


def send(cmd):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    sock.connect(('127.0.0.1', 9876))
    sock.sendall((json.dumps(cmd) + '\n').encode())
    buf = b''
    while b'\n' not in buf:
        chunk = sock.recv(65536)
        if not chunk:
            break
        buf += chunk
    sock.close()
    return json.loads(buf.decode().strip())


def get_labels():
    result = send({'action': 'widget_tree'})
    if not result.get('ok'):
        return []
    labels = []
    def find(node):
        t = node.get('text', '')
        if t and len(t) > 1 and not t.startswith('#'):
            labels.append(t)
        for c in node.get('children', []):
            find(c)
    find(result['tree'])
    return labels


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == 'ping':
        print(send({'action': 'ping'}))

    elif cmd == 'state':
        r = send({'action': 'get_state'})
        if r.get('ok'):
            print(f"menu: {r['ui']['current_menu_id']}")
            print(f"history: {r['ui']['history']}")
            print(f"seed_loaded: {r['specter']['seed_loaded']}")
            print(f"is_locked: {r['specter']['is_locked']}")
        else:
            print(r)

    elif cmd == 'click':
        if len(sys.argv) < 3:
            print('Usage: click "Button Text"')
            return
        text = sys.argv[2]
        send({'action': 'click', 'text': text})
        r = send({'action': 'get_state'})
        print(f"-> {r['ui']['current_menu_id']} (history: {r['ui']['history']})")

    elif cmd == 'labels':
        for label in get_labels():
            print(f"  {label}")

    elif cmd == 'set':
        if len(sys.argv) < 4:
            print('Usage: set attr value')
            return
        attr, val = sys.argv[2], sys.argv[3]
        # Parse value
        if val.lower() == 'true':
            val = True
        elif val.lower() == 'false':
            val = False
        elif val.isdigit():
            val = int(val)
        print(send({'action': 'set_state', 'attr': attr, 'value': val}))

    elif cmd == 'tree':
        print(json.dumps(send({'action': 'widget_tree'}), indent=2))

    elif cmd == 'screenshot':
        from PIL import Image
        import struct

        out_filename = sys.argv[2] if len(sys.argv) > 2 else '/tmp/sim_screenshot.png'
        r = send({'action': 'screenshot'})

        if not r.get('ok'):
            print(f"Error: {r.get('error', 'unknown')}")
            return

        w, h = r['width'], r['height']
        raw_file = r.get('file')

        if raw_file:
            # Read raw RGB565 data from file
            with open(raw_file, 'rb') as f:
                raw = f.read()
        else:
            # Fallback: base64 data in response
            raw = base64.b64decode(r['data'])

        # Convert RGB565 to RGB
        pixels = bytearray(w * h * 3)
        for i in range(0, len(raw), 2):
            if i + 1 >= len(raw):
                break
            pixel = struct.unpack('<H', raw[i:i+2])[0]
            rv = ((pixel >> 11) & 0x1F) << 3
            gv = ((pixel >> 5) & 0x3F) << 2
            bv = (pixel & 0x1F) << 3
            idx = (i // 2) * 3
            pixels[idx] = rv
            pixels[idx + 1] = gv
            pixels[idx + 2] = bv

        img = Image.frombytes('RGB', (w, h), bytes(pixels))
        img.save(out_filename, 'PNG')
        print(f"Screenshot saved to {out_filename} ({w}x{h})")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()

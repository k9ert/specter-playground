#!/usr/bin/env python3
"""CLI for LVGL simulator control."""
import socket
import json
import base64
import os
import click


# --- Core functions ---

def send(cmd):
    """Send command to simulator and return JSON response."""
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
    """Extract visible text labels from widget tree."""
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


def save_screenshot(out_filename):
    """Save screenshot to file. Returns (width, height) or None on error."""
    from PIL import Image
    import struct

    r = send({'action': 'screenshot'})
    if not r.get('ok'):
        return None

    w, h = r['width'], r['height']
    raw_file = r.get('file')

    if raw_file:
        with open(raw_file, 'rb') as f:
            raw = f.read()
    else:
        raw = base64.b64decode(r['data'])

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
    return (w, h)


def get_state():
    """Get current UI and Specter state."""
    return send({'action': 'get_state'})


def navigate(target):
    """Navigate to menu or back."""
    return send({'action': 'navigate', 'target': target})


# --- CLI Commands ---

@click.group()
def cli():
    """LVGL Simulator CLI - control the MockUI simulator."""
    pass


@cli.command()
def ping():
    """Test connection to simulator."""
    click.echo(send({'action': 'ping'}))


@cli.command()
def state():
    """Show current UI state."""
    r = get_state()
    if r.get('ok'):
        click.echo(f"menu: {r['ui']['current_menu_id']}")
        click.echo(f"history: {r['ui']['history']}")
        click.echo(f"seed_loaded: {r['specter']['seed_loaded']}")
        click.echo(f"is_locked: {r['specter']['is_locked']}")
    else:
        click.echo(r)


@cli.command('click')
@click.argument('text')
def click_cmd(text):
    """Click a button by its text label."""
    send({'action': 'click', 'text': text})
    r = get_state()
    click.echo(f"-> {r['ui']['current_menu_id']} (history: {r['ui']['history']})")


@cli.command()
def labels():
    """List visible text labels."""
    for label in get_labels():
        click.echo(f"  {label}")


@cli.command('set')
@click.argument('attr')
@click.argument('value')
def set_cmd(attr, value):
    """Set a state attribute (e.g., seed_loaded, is_locked)."""
    # Parse value
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif value.isdigit():
        value = int(value)
    click.echo(send({'action': 'set_state', 'attr': attr, 'value': value}))


@cli.command()
def tree():
    """Dump full widget tree as JSON."""
    click.echo(json.dumps(send({'action': 'widget_tree'}), indent=2))


@cli.command()
def back():
    """Navigate back to previous menu."""
    navigate('back')
    r = get_state()
    click.echo(f"-> {r['ui']['current_menu_id']} (history: {r['ui']['history']})")


@cli.command('goto')
@click.argument('menu_id')
def goto_cmd(menu_id):
    """Navigate directly to a menu by ID."""
    navigate(menu_id)
    r = get_state()
    click.echo(f"-> {r['ui']['current_menu_id']} (history: {r['ui']['history']})")


@cli.command()
@click.argument('filename', required=False)
def screenshot(filename):
    """Capture screenshot to PNG file."""
    screenshot_dir = '/tmp/specter-playground_agent/screenshots'
    os.makedirs(screenshot_dir, exist_ok=True)
    out_filename = filename or f'{screenshot_dir}/screenshot.png'
    result = save_screenshot(out_filename)
    if result:
        click.echo(f"Screenshot saved to {out_filename} ({result[0]}x{result[1]})")
    else:
        click.echo("Error: screenshot failed", err=True)


@cli.command()
@click.argument('folder')
def capture(folder):
    """Capture screenshot, labels, and tree to a folder."""
    os.makedirs(folder, exist_ok=True)

    # Screenshot
    result = save_screenshot(f'{folder}/screenshot.png')
    if result:
        click.echo(f"  screenshot.png ({result[0]}x{result[1]})")
    else:
        click.echo("  screenshot.png FAILED", err=True)

    # Labels
    lbls = get_labels()
    with open(f'{folder}/labels.txt', 'w') as f:
        for label in lbls:
            f.write(f"  {label}\n")
    click.echo(f"  labels.txt ({len(lbls)} labels)")

    # Tree
    tree_data = send({'action': 'widget_tree'})
    with open(f'{folder}/tree.json', 'w') as f:
        json.dump(tree_data, f, indent=2)
    click.echo(f"  tree.json")

    click.echo(f"Captured to {folder}/")


@cli.command()
def restart():
    """Restart the simulator process."""
    import subprocess
    import time

    # Kill existing simulator
    subprocess.run(['pkill', '-f', 'micropython_unix.*mock_ui'], capture_output=True)
    time.sleep(1)

    # Start new one
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    subprocess.Popen(
        [f'{project_root}/bin/micropython_unix', f'{project_root}/scenarios/mock_ui.py', '--control'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(2)

    # Verify
    try:
        r = send({'action': 'ping'})
        click.echo(f"Simulator restarted: {r}")
    except Exception:
        click.echo("Failed to restart simulator", err=True)


def get_project_root():
    """Get project root directory."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@cli.command()
@click.argument('folder', required=False)
@click.option('--max-depth', default=5, help='Maximum navigation depth')
def explore(folder, max_depth):
    """Recursively explore all screens and capture to folder.

    Navigates through all menus, captures screenshot/labels/tree for each.
    Creates subfolder structure matching menu hierarchy.

    Default output: docs/MockUI/screens/
    """
    if not folder:
        folder = os.path.join(get_project_root(), 'docs/MockUI/screens')

    os.makedirs(folder, exist_ok=True)
    visited = set()

    def capture_screen(menu_id):
        """Capture current screen."""
        path = os.path.join(folder, menu_id)
        os.makedirs(path, exist_ok=True)

        result = save_screenshot(f'{path}/screenshot.png')
        if result:
            click.echo(f"  {menu_id}/screenshot.png ({result[0]}x{result[1]})")

        lbls = get_labels()
        with open(f'{path}/labels.txt', 'w') as f:
            for label in lbls:
                f.write(f"  {label}\n")

        tree_data = send({'action': 'widget_tree'})
        with open(f'{path}/tree.json', 'w') as f:
            json.dump(tree_data, f, indent=2)

        return lbls

    def explore_menu(depth=0):
        """Recursively explore current menu."""
        if depth > max_depth:
            return

        state = get_state()
        menu_id = state['ui']['current_menu_id']

        if menu_id in visited:
            return
        visited.add(menu_id)

        click.echo(f"Exploring: {menu_id} (depth {depth})")
        labels = capture_screen(menu_id)

        # Filter to likely menu items
        menu_items = [l for l in labels if len(l) > 2 and not l.isdigit()
                      and l not in ('eng', 'OK', 'Cancel', 'Back')
                      and not l.endswith(':')]

        for item in menu_items:
            try:
                send({'action': 'click', 'text': item})
                new_state = get_state()
                new_menu = new_state['ui']['current_menu_id']

                if new_menu != menu_id and new_menu not in visited:
                    explore_menu(depth + 1)

                # Return to current menu
                navigate('back')
                back_state = get_state()
                if back_state['ui']['current_menu_id'] != menu_id:
                    navigate(menu_id)

            except Exception as e:
                click.echo(f"  Error exploring '{item}': {e}", err=True)

    # Start from main
    navigate('main')
    explore_menu()

    click.echo(f"\nExplored {len(visited)} screens to {folder}/")


if __name__ == '__main__':
    cli()

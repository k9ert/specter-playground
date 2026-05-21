"""Widget tree extraction for LVGL."""
import lvgl as lv


def get_widget_info(obj):
    """Extract info from single widget."""
    info = {
        "type": type(obj).__name__,
        "x": obj.get_x(),
        "y": obj.get_y(),
        "width": obj.get_width(),
        "height": obj.get_height(),
        "text": None,
        "children": [],
    }
    # Try to get text for labels
    if hasattr(obj, "get_text"):
        try:
            info["text"] = obj.get_text()
        except:
            pass
    return info


def get_widget_tree(obj):
    """Recursively build widget tree from LVGL object."""
    info = get_widget_info(obj)
    child_count = obj.get_child_count()
    for i in range(child_count):
        child = obj.get_child(i)
        info["children"].append(get_widget_tree(child))
    return info


def find_widget_at(obj, x, y, abs_x=0, abs_y=0):
    """Find deepest clickable widget at absolute screen coords (x, y).
    
    Returns the widget or None. Walk children last-to-first so topmost (last drawn)
    wins, matching LVGL hit-test order.
    """
    # Compute this object's absolute origin
    cur_abs_x = abs_x + obj.get_x()
    cur_abs_y = abs_y + obj.get_y()
    w = obj.get_width()
    h = obj.get_height()

    # Skip hidden objects
    try:
        if obj.has_flag(lv.obj.FLAG.HIDDEN):
            return None
    except:
        pass

    # Not within bounds → skip entire subtree
    if not (cur_abs_x <= x <= cur_abs_x + w and cur_abs_y <= y <= cur_abs_y + h):
        return None

    # Check children last-to-first (topmost wins)
    child_count = obj.get_child_count()
    for i in range(child_count - 1, -1, -1):
        try:
            child = obj.get_child(i)
            if child is None:
                continue
            result = find_widget_at(child, x, y, cur_abs_x, cur_abs_y)
            if result is not None:
                return result
        except:
            pass

    # This widget contains the point
    return obj


def find_widget_by_text(obj, text, parent=None):
    """Find widget containing label with given text. Returns (widget, parent)."""
    # Check if this is a label with matching text
    if hasattr(obj, "get_text"):
        try:
            if obj.get_text() == text:
                # Return parent (the button) if exists, else the label itself
                return (parent if parent else obj, obj)
        except:
            pass

    # Recurse into children
    child_count = obj.get_child_count()
    for i in range(child_count):
        child = obj.get_child(i)
        result = find_widget_by_text(child, text, obj)
        if result[0]:
            return result

    return (None, None)

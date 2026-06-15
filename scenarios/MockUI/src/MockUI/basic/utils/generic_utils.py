"""generic utils."""


def resolve_obj(path, root):
    """Walk *path* starting from *root* and return the final value.

    E.g. given path "a.b[foo].c" this does:
    1. current = root
    2. current = getattr(current, "a", None)
    3. current = getattr(current, "b", None)
    4. current = current["foo"] (also tries int("foo") if current is list/tuple)
    5. current = getattr(current, "c", None)

    Each dot-separated segment is either:
      - a plain attribute name  → ``getattr(current, segment)``
      - ``attr[key]``           → ``getattr(current, attr)[key]``

    For list/tuple subscripts the key is also tried as an ``int``.

    Returns the resolved value, or ``None`` if any segment fails.
    """
    current = root
    for segment in path.split("."):
        if "[" in segment:
            attr, _, rest = segment.partition("[")
            key = rest.rstrip("]").strip("\"'")
            # step 1: get the attribute (may itself be absent)
            if attr:
                current = getattr(current, attr, None)
                if current is None:
                    return None
            # step 2: subscript — try int index for sequences
            if isinstance(current, (list, tuple)):
                try:
                    key = int(key)
                except (ValueError, TypeError):
                    pass
            try:
                current = current[key]
            except (KeyError, IndexError, TypeError):
                return None
        else:
            current = getattr(current, segment, None)
            if current is None:
                return None
    return current

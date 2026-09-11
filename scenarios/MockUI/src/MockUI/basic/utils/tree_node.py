"""TreeNode — minimal reference-based tree node for generic tree data-
structures.

Callers build and own the nodes: ``item`` is referenced (never copied)
Structure is stored as parent/children references only;
derived facts like depth or leaf-ness are computed on demand.
"""


class TreeNode:
    """One node in a tree or forest.

    Attributes:
        item:     Caller-owned payload/data item, 
                  stored by reference only.
        key:      Stable unique identifier.
        parent:   Parent ``TreeNode`` or ``None`` for forest roots.
        children: List of child ``TreeNode`` objects, [] for leaves.
    """

    def __init__(self, item, parent=None, children=None, key=None):
        self.item = item
        self.key = item if key is None else key
        self.parent = parent
        self.children = children if children is not None else []

    def add_child(self, child):
        """Bidirectionally link *child* below this node.

        Re-linking the same child to the same parent is a no-op; linking a
        child that already has a different parent raises ``ValueError``.
        """
        if child.parent is self:
            return
        if child.parent is not None:
            raise ValueError(
                "%r is claimed as child by multiple parents" % (child.item,))
        child.parent = self
        self.children.append(child)

    def has_children(self):
        """Return whether this node has linked children."""
        return bool(self.children)

    def depth(self):
        """Compute hierarchy depth by walking parent links to the root."""
        depth = 0
        node = self.parent
        while node is not None:
            depth += 1
            node = node.parent
        return depth


def build_forest(items, get_parent=None, get_children=None, make_key=None):
    """Build a list of root ``TreeNode`` objects from a flat item list.

    *items* are stored by reference (never copied). Links may be declared from
    either or both sides:

    * ``get_parent(item)``   → parent item or ``None`` for roots.
    * ``get_children(item)`` → iterable of child items (or ``None``).
    * ``make_key(item)``     → stable unique key for expansion state etc.
      Defaults to the item itself. Duplicate keys raise ``ValueError``.

    When only one side is given, the forest is derived from it directly.  When
    both are given, the declarations must be consistent; contradictions,
    duplicates, unknown links and cycles raise ``ValueError`` naming the
    offending items.  When neither is given, every item becomes a root.

    """
    if get_parent is not None and not callable(get_parent):
        raise TypeError("get_parent must be callable or None")
    if get_children is not None and not callable(get_children):
        raise TypeError("get_children must be callable or None")
    if make_key is not None and not callable(make_key):
        raise TypeError("make_key must be callable or None")

    def _key(item):
        return item if make_key is None else make_key(item)

    nodes_by_key = {}
    for item in items:
        key = _key(item)
        if key in nodes_by_key:
            raise ValueError("duplicate key in tree input: %r" % (key,))
        nodes_by_key[key] = TreeNode(item, key=key)

    roots = []

    # Parent pass: links come from get_parent declarations.
    if get_parent is not None:
        for item in items:
            node = nodes_by_key[_key(item)]
            parent_item = get_parent(item)
            if parent_item is None:
                continue
            parent_node = nodes_by_key.get(_key(parent_item))
            if parent_node is None:
                raise ValueError("parent %r of %r is not in the item list"
                                 % (parent_item, item))
            parent_node.add_child(node)

    # Children pass: links come from get_children declarations.
    if get_children is not None:
        for item in items:
            node = nodes_by_key[_key(item)]
            for child_item in get_children(item) or ():
                child_node = nodes_by_key.get(_key(child_item))
                if child_node is None:
                    raise ValueError("child %r of %r is not in the item list"
                                     % (child_item, item))
                node.add_child(child_node)

    # Mixed consistency: every parent-declared link must also appear in the
    # parent's get_children declaration.  The reverse direction is already
    # covered by add_child's double-parent guard during the children pass.
    if get_parent is not None and get_children is not None:
        for item in items:
            node = nodes_by_key[_key(item)]
            if node.parent is None:
                continue
            found = False
            for child_item in get_children(node.parent.item) or ():
                if _key(child_item) == node.key:
                    found = True
                    break
            if not found:
                raise ValueError(
                    "contradictory links: %r declares parent %r, "
                    "but %r does not list it as a child"
                    % (item, node.parent.item, node.parent.item))

    for item in items:
        node = nodes_by_key[_key(item)]
        if node.parent is None:
            roots.append(node)

    # Cycle / orphan detection: every node must be reachable from a root.
    reached = 0
    stack = list(roots)
    while stack:
        node = stack.pop()
        reached += 1
        stack.extend(node.children)
    if reached != len(items):
        raise ValueError("tree input contains a cycle or disconnected nodes")

    return roots


def flatten_forest(roots):
    """Return all nodes of *roots* as a flat list in stable preorder.
    """
    nodes = []
    stack = list(reversed(roots))
    while stack:
        node = stack.pop()
        nodes.append(node)
        stack.extend(reversed(node.children))
    return nodes

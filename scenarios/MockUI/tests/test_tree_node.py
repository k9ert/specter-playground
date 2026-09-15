import pytest

from MockUI.basic.utils.tree_node import TreeNode, build_forest, flatten_forest


def test_build_forest_handles_empty_and_singleton_inputs():
    assert build_forest([]) == []

    roots = build_forest(["only item"])

    assert [node.item for node in roots] == ["only item"]
    assert [node.item for node in flatten_forest(roots)] == ["only item"]


def test_add_child_links_nodes_and_calculates_depth():
    root = TreeNode("root")
    child = TreeNode("child")
    grandchild = TreeNode("grandchild")

    root.add_child(child)
    child.add_child(grandchild)

    assert child.parent is root
    assert grandchild.parent is child
    assert root.has_children() is True
    assert grandchild.has_children() is False
    assert grandchild.depth() == 2


def test_add_child_does_not_duplicate_an_existing_link():
    parent = TreeNode("parent")
    child = TreeNode("child")

    parent.add_child(child)
    parent.add_child(child)

    assert parent.children == [child]
    assert child.parent is parent


def test_add_child_rejects_a_second_parent():
    first_parent = TreeNode("first parent")
    second_parent = TreeNode("second parent")
    child = TreeNode("child")
    first_parent.add_child(child)

    with pytest.raises(ValueError, match="multiple parents"):
        second_parent.add_child(child)

    assert first_parent.children == [child]
    assert second_parent.children == []


def test_build_forest_from_parent_callback_preserves_preorder():
    items = ["root", "child", "grandchild", "second root"]
    parents = {"root": None, "child": "root", "grandchild": "child",
               "second root": None}

    roots = build_forest(items, get_parent=parents.get)

    assert [node.item for node in roots] == ["root", "second root"]
    assert [node.item for node in flatten_forest(roots)] == items


def test_build_forest_from_children_callback_preserves_preorder():
    items = ["root", "child", "grandchild", "second root"]
    children = {"root": ["child"], "child": ["grandchild"],
                "grandchild": [], "second root": []}

    roots = build_forest(items, get_children=children.get)

    assert [node.item for node in roots] == ["root", "second root"]
    assert [node.item for node in flatten_forest(roots)] == items


def test_build_forest_accepts_unhashable_items_with_stable_custom_keys():
    root = {"key": "root"}
    child = {"key": "child"}
    items = [root, child]

    roots = build_forest(
        items,
        get_parent=lambda item: root if item is child else None,
        make_key=lambda item: item["key"],
    )

    assert roots[0].item is root
    assert roots[0].children[0].item is child
    assert roots[0].children[0].key == "child"


@pytest.mark.parametrize(
    "argument",
    [
        {"get_parent": object()},
        {"get_children": object()},
        {"make_key": object()},
    ],
)
def test_build_forest_rejects_non_callable_callbacks(argument):
    with pytest.raises(TypeError, match="callable or None"):
        build_forest(["item"], **argument)


def test_build_forest_rejects_duplicate_keys():
    with pytest.raises(ValueError, match="duplicate key"):
        build_forest(["first", "second"], make_key=lambda item: "same")


def test_build_forest_rejects_unknown_parent():
    with pytest.raises(ValueError, match="parent .*not in the item list"):
        build_forest(["child"], get_parent=lambda item: "missing")


def test_build_forest_rejects_children_with_multiple_parents():
    children = {"first": ["child"], "second": ["child"], "child": []}

    with pytest.raises(ValueError, match="multiple parents"):
        build_forest(["first", "second", "child"], get_children=children.get)


def test_build_forest_rejects_unknown_children():
    with pytest.raises(ValueError, match="not in the item list"):
        build_forest(["root"], get_children=lambda item: ["unknown"])


@pytest.mark.parametrize(
    "parents",
    [
        {"item": "item"},
        {"first": "second", "second": "first"},
    ],
)
def test_build_forest_rejects_self_and_parent_cycles(parents):
    with pytest.raises(ValueError, match="cycle"):
        build_forest(list(parents), get_parent=parents.get)


@pytest.mark.parametrize(
    "parents, children",
    [
        ({"parent": None, "child": "parent"},
         {"parent": [], "child": []}),
        ({"parent": None, "child": None},
         {"parent": ["child"], "child": []}),
    ],
)
def test_build_forest_rejects_contradictory_mixed_declarations(
        parents, children):
    with pytest.raises(ValueError, match="contradictory links"):
        build_forest(
            ["parent", "child"],
            get_parent=parents.get,
            get_children=children.get,
        )
from MockUI.basic.utils.tree_node import build_forest
from MockUI.stubs.seed import Seed


def test_active_passphrase_fingerprint_detaches_bip85_descendants():
    parent = Seed("Renamed Parent", fingerprint="b07b0001",
                  passphrase="correct horse", passphrase_active=True)
    child = Seed("Unrelated Label", fingerprint="b07b0002")
    grandchild = Seed("Another Label", fingerprint="b07b000b")
    all_seeds = [parent, child, grandchild]

    forest = build_forest(
        all_seeds,
        get_children=lambda seed: seed.known_bip85_derivations(all_seeds),
        make_key=lambda seed: seed.get_fingerprint(),
    )

    assert parent.get_fingerprint() == "1000b70b"
    assert [node.item for node in forest] == [parent, child]
    assert forest[0].children == []
    assert [node.item for node in forest[1].children] == [grandchild]
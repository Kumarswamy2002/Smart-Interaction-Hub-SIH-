from sih.security.merkle_audit import MerkleAuditTree

def test_merkle_root_computation():
    leaves = ["event-1: login", "event-2: prompt", "event-3: action"]
    root = MerkleAuditTree.compute_root(leaves)
    assert len(root) == 64
    assert root == MerkleAuditTree.compute_root(leaves)

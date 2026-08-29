"""
Merkle Tree Audit & Cryptographic Log Verifier
"""
import hashlib
from typing import List

class MerkleAuditTree:
    @staticmethod
    def hash_leaf(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @classmethod
    def compute_root(cls, leaves: List[str]) -> str:
        if not leaves:
            return ""
        current_level = [cls.hash_leaf(l) for l in leaves]
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i+1] if i+1 < len(current_level) else left
                combined = hashlib.sha256((left + right).encode('utf-8')).hexdigest()
                next_level.append(combined)
            current_level = next_level
        return current_level[0]

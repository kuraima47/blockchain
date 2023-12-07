from .mpt.mpt import MerklePatriciaTrie
from .mpt.hash import keccak_hash


class Storage:

    def __init__(self, storage_root=None, in_memory=False):
        self.storage = "blockchain/mpt/lvlDB/DB/"
        self.current_root = storage_root
        self._in_memory = in_memory

    def set_root(self, root):
        self.current_root = root

    def save(self, data={}):
        self._in_memory = False
        self.current_root = None
        for k, v in data:
            self[k] = v

    def __getitem__(self, key):
        trie = MerklePatriciaTrie(self.storage, in_memory=self._in_memory, root=self.current_root)
        try:
            return trie.get(keccak_hash(key))
        except KeyError:
            return None

    def __setitem__(self, key, value):
        trie = MerklePatriciaTrie(self.storage, in_memory=self._in_memory, root=self.current_root)
        trie.update(keccak_hash(key), value)
        self.current_root = trie.root_hash()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

from .mpt.mpt import MerklePatriciaTrie


class Storage:

    def __init__(self, storage_root=None):
        self.storage = "blockchain/mpt/lvlDB/DB/"
        self.current_root = storage_root

    def set_root(self, root):
        self.current_root = root

    def __getitem__(self, key):
        trie = MerklePatriciaTrie(self.storage, root=self.current_root)
        try:
            return trie.get(key)
        except KeyError:
            return None

    def __setitem__(self, key, value):
        trie = MerklePatriciaTrie(self.storage, root=self.current_root)
        trie.update(key, value)
        self.current_root = trie.root_hash()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

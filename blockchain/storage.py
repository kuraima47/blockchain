from .mpt.mpt import MerklePatriciaTrie


class Storage:

    def __init__(self):
        self.storage = "blockchain/mpt/lvlDB/DB/"
        self.trie = MerklePatriciaTrie(self.storage)

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
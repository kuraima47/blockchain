from trie.mpt import MerklePatriciaTrie


class Storage:

    def __init__(self):
        self.storage = {}
        self.trie = MerklePatriciaTrie(self.storage)

    def test(self):
        self.trie.update(b'do', b'verb')
        self.trie.update(b'dog', b'puppy')
        self.trie.update(b'doge', b'coin')
        self.trie.update(b'horse', b'stallion')
        old_root = self.trie.root()
        old_root_hash = self.trie.root_hash()

        print("Root hash is {}".format(old_root_hash.hex()))

        self.trie.delete(b'doge')

        print("New root hash is {}".format(self.trie.root_hash().hex()))

        trie_from_old_hash = MerklePatriciaTrie(self.storage, root=old_root)

        print(trie_from_old_hash.get(b'doge'))

        try:
            print(self.trie.get(b'doge'))
        except KeyError:
            print('Not accessible in a new trie.')


if __name__ == '__main__':
    storage = Storage()
    storage.test()

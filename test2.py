from blockchain.transaction import Transaction
from blockchain.block import Block
# b.add_transaction(Transaction(0, 0, b'', 0, b''))


class Blockchain:
    chain = []

    def __init__(self):
        genesis = Block((0, b'', b'', b'', 0, 0, 0, 0, 0, b'', b'', b'', b''), [])
        self.chain.append(genesis.encode_block)

    def add(self, block):
        self.chain.append(block.encode_block)

    @property
    def last_hash(self):
        last = Block.decode_block(self.chain[-1])
        return last.hash

    def __repr__(self):
        return f"<{self.__class__.__name__} #{len(self.chain)} blocks={self.chain}>"


blockchain = Blockchain()
print(blockchain)
b = Block((1, blockchain.last_hash, b'', b'', 0, 0, 0, 0, 0, b'', b'', b'', b''), [])
b.add_transaction(Transaction(0, 0, b'', 0, b''))
print(b)
b.add_transaction(Transaction(0, 0, b'', 0, b''))
print(b)
blockchain.add(b)
print(blockchain)

b = Block((2, blockchain.last_hash, b'', b'', 0, 0, 0, 0, 0, b'', b'', b'', b''), [])
b.add_transaction(Transaction(0, 0, b'', 0, b''))
print(b)
b.add_transaction(Transaction(0, 0, b'', 0, b''))
print(b)
blockchain.add(b)
print(blockchain)

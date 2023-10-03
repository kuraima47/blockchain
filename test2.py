from blockchain.transaction import Transaction
from blockchain.block import Block


b = Block((12, b'', b'', b'', 0, b'\x00' * 8, 0, 0, 0, b'', b'', b'', b''), [])
b.add_transaction(Transaction(0, 0, 0, b'', 0, b''))
b.add_transaction(Transaction(0, 0, 0, b'', 0, b''))
print(b)
print(b.get_transaction(0))
print(b.head.number)

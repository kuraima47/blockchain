from blockchain.transaction import Transaction
from blockchain.block import Block

print(f"----------Encoded Block----------")
b = Block((12, b'', b'', b'', 0, 0, 0, 0, 0, b'', b'', b'', b''), [])
b.add_transaction(Transaction(0, 0, b'', 0, b''))
b.add_transaction(Transaction(0, 0, b'', 0, b''))
enc = b.encode_block
print(b)
print(b.get_transaction(0))
print("---------------------------------")
print(f"encrypted : {enc}")
print(f"----------Decoded Block----------")
dec_b = Block.decode_block(enc)
print(dec_b)
print(dec_b.get_transaction(0))

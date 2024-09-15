import rlp
from kademlia.crypto import sha3
from kademlia.utils import decode_hex
from blockchain.transaction import Transaction
from .storage import Storage


class Block(rlp.Serializable):
    fields = [
        ("header", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("transactions", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("uncles", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("withdrawals", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self, header, transactions=(), uncles=(), withdrawals=()):
        if not isinstance(header, BlockHeader):
            header = BlockHeader(*header)
        super(Block, self).__init__(header, transactions, uncles, withdrawals)

    @property
    def hash(self) -> bytes:
        return sha3(sha3(rlp.encode([
            ("header", self.header),
            ("transactions", self.transactions)
        ])))[::-1]

    def __repr__(self):
        return (f"<{self.__class__.__name__} "
                f"#{self.header.number} "
                f"hash={self.hash.hex()} "
                f"transactions={len(self.transactions)}>"
                )

    def add_transaction(self, tx) -> None:
        t = tx.encode_transaction
        self.__dict__['_transactions'] += t,
        self.header.transaction_storage[tx.hash] = t
        self.header.transaction_root = self.header.transaction_storage.current_root

    @property
    def is_valid_block(self) -> bool:
        valid = self.validate_transactions()
        if valid:
            self.save_transactions()
        return valid

    def validate_transactions(self) -> bool:
        for tx in self.transactions:
            tr = rlp.decode(tx, Transaction)
            if not tr.is_valid:
                return False
        if self.header.transaction_root != self.header.transaction_storage.current_root:
            return False
        return True

    def mine(self, difficulty: bytes) -> bytes:
        while self.hash >= difficulty:
            self.header.nonce += 1
        return self.hash

    @property
    def encode_block(self) -> str:
        return rlp.encode([self.header, self.transactions]).hex()

    @classmethod
    def decode_block(cls, hex_block: str):
        return rlp.decode(decode_hex(hex_block), cls)

    def get_transaction(self, index) -> Transaction:
        return Transaction.decode_transaction(self.transactions[index])

    @property
    def head(self):
        return self.header

    def save_transactions(self):
        d = {tx.hash: self.header.transaction_storage[tx.hash] for tx in self.transactions}
        self.header.transaction_storage.save(d)


class BlockHeader(rlp.Serializable):
    fields = [
        ("number", rlp.sedes.big_endian_int),
        ("parent_hash", rlp.sedes.binary),
        ("uncles_hash", rlp.sedes.binary),
        ("beneficiary", rlp.sedes.binary),
        ("difficulty", rlp.sedes.big_endian_int),
        ("nonce", rlp.sedes.big_endian_int),
        ("gas_limit", rlp.sedes.big_endian_int),
        ("gas_used", rlp.sedes.big_endian_int),
        ("timestamp", rlp.sedes.big_endian_int),
        ("transaction_root", rlp.sedes.binary),
        ("state_root", rlp.sedes.binary),
        ("receipts_root", rlp.sedes.binary),
        ("logs_bloom", rlp.sedes.binary),
        ("extra_data", rlp.sedes.binary),
    ]

    def __init__(self, number, parent_hash, uncles_hash, beneficiary, difficulty, nonce, gas_limit, gas_used, timestamp,
                 transaction_root, state_root, receipts_root, logs_bloom, extra_data=b''):

        self.state_storage = Storage(state_root, True)
        self.transaction_storage = Storage(in_memory=True) if transaction_root is b'' else Storage(transaction_root, True)
        self.receipts_storage = Storage(in_memory=True) if receipts_root is b'' else Storage(receipts_root, True)

        if not isinstance(number, int):
            number = int.from_bytes(number, 'big')
        if not isinstance(difficulty, int):
            difficulty = int.from_bytes(difficulty, 'big')
        if not isinstance(nonce, int):
            nonce = int.from_bytes(nonce, 'big')
        if not isinstance(gas_limit, int):
            gas_limit = int.from_bytes(gas_limit, 'big')
        if not isinstance(gas_used, int):
            gas_used = int.from_bytes(gas_used, 'big')
        if not isinstance(timestamp, int):
            timestamp = int.from_bytes(timestamp, 'big')

        super(BlockHeader, self).__init__(number, parent_hash, uncles_hash, beneficiary, difficulty, nonce,
                                          gas_limit, gas_used, timestamp, transaction_root, state_root, receipts_root,
                                          logs_bloom, extra_data)

    def __repr__(self) -> str:
        return rlp.encode(self).hex()

    @property
    def hash(self) -> bytes:
        return sha3(sha3(rlp.encode(self)))[::-1]


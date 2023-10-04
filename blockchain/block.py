import rlp
from crypto import sha3
from utils import decode_hex
from blockchain.transaction import Transaction


class Block(rlp.Serializable):
    fields = [
        ("header", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("transactions", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self, header, transactions=[]):
        super(Block, self).__init__(BlockHeader(*header), transactions)

    @property
    def hash(self) -> bytes:
        return sha3(rlp.encode([
            ("header", self.header),
            ("transactions", self.transactions)
        ]))

    def __repr__(self):
        return f"<Block #{self.header.number} hash={self.hash.hex()} transactions={len(self.transactions)}>"

    def add_transaction(self, tx) -> None:
        self.__dict__['_transactions'] += tx.encode_transaction,

    @property
    def is_valid_block(self) -> bool:
        self.validate_transactions()
        return True

    def validate_transactions(self) -> bool:
        for tx in self.transactions:
            tr = rlp.decode(tx, Transaction)
            if not tr.is_valid:
                return False
        return True

    @property
    def encode_block(self) -> str:
        return rlp.encode([self.header, self.transactions]).hex()

    @classmethod
    def decode_block(cls, hex_block: str):
        return rlp.decode(decode_hex(hex_block), cls)

    def get_transaction(self, index):
        if isinstance(self.transactions[index], bytes):
            return Transaction.decode_transaction(self.transactions[index].decode("utf-8"))
        return Transaction.decode_transaction(self.transactions[index])

    @property
    def head(self):
        return self.header


class BlockHeader(rlp.Serializable):
    fields = [
        ("number", rlp.sedes.big_endian_int),
        ("parent_hash", rlp.sedes.binary),
        ("ommers_hash", rlp.sedes.binary),
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
    ]

    def __init__(self, number, parent_hash, ommers_hash, beneficiary, difficulty, nonce, gas_limit, gas_used, timestamp,
                 transaction_root, state_root, receipts_root, logs_bloom):

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

        super(BlockHeader, self).__init__(number, parent_hash, ommers_hash, beneficiary, difficulty, nonce, gas_limit,
                                          gas_used, timestamp, transaction_root, state_root, receipts_root, logs_bloom)

    def __repr__(self) -> str:
        return rlp.encode(self).hex()

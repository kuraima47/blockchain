import rlp
from crypto import sha3
from utils import decode_hex
from transaction import Transaction


class Block(rlp.Serializable):
    fields = [
        ("header", rlp.sedes.binary),
        ("transactions", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self):
        header = BlockHeader(**{
            "number": 0,
            "parent_hash": b'',
            "ommers_hash": b'',
            "beneficiary": b'',
            "difficulty": 0,
            "nonce": b'\x00' * 8,
            "gas_limit": 0,
            "gas_used": 0,
            "timestamp": 0,
            "transaction_root": b'',
            "state_root": b'',
            "receipts_root": b'',
            "logs_bloom": b''
        })
        transactions = []

        super(Block, self).__init__(header, transactions)

    @property
    def hash(self):
        return sha3(rlp.encode([
            ("header", self.header),
            ("transactions", self.transactions)
        ]))

    def __repr__(self):
        return f"<Block #{self.header.number} hash={self.hash.hex()} transactions={len(self.transactions)}>"

    def add_transaction(self, tx):
        self.transactions.append(tx)

    @property
    def is_valid_block(self):
        self.validate_transactions()
        return True

    def validate_transactions(self):
        for tx in self.transactions:
            tr = rlp.decode(tx, Transaction)
            if not tr.is_valid:
                return False
        return True

    def encode_block(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode_block(cls, hex_block):
        return rlp.decode(decode_hex(hex_block), cls)


class BlockHeader(rlp.Serializable):
    fields = [
        ("number", rlp.sedes.big_endian_int),
        ("parent_hash", rlp.sedes.binary),
        ("ommers_hash", rlp.sedes.binary),
        ("beneficiary", rlp.sedes.binary),
        ("difficulty", rlp.sedes.big_endian_int),
        ("nonce", rlp.sedes.binary),
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
        super(BlockHeader, self).__init__(number, parent_hash, ommers_hash, beneficiary, difficulty, nonce, gas_limit,
                                          gas_used, timestamp, transaction_root, state_root, receipts_root, logs_bloom)

    def __repr__(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode_header(cls, hex_header):
        return rlp.decode(decode_hex(hex_header), cls)

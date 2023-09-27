import rlp
import utils


class Block(rlp.Serializable):

    fields = [
        ("header", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("transactions", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self):
        header = {
            "number": 0,
            "parent_hash": "",
            "ommers_hash": "",
            "beneficiary": "",
            "difficulty": 0,
            "nonce": 0x0,
            "gas_limit": 0,
            "gas_used": 0,
            "timestamp": 0,
            "transaction_root": "",
            "state_root": "",
            "receipts_root": "",
            "logs_bloom": "",
        }
        transactions = []

        super(Block, self).__init__(header, transactions)

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self))

    def __repr__(self):
        return f"<Block #{self.number} hash={self.hash} {len(self.transactions)} transactions>"

    def to_dict(self):
        return {
            "number": self.number,
            "parent_hash": self.parent_hash,
            "ommers_hash": self.ommers_hash,
            "beneficiary": self.beneficiary,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
            "gas_used": self.gas_used,
            "timestamp": self.timestamp,
            "transaction_root": self.transaction_root,
            "state_root": self.state_root,
            "receipts_root": self.receipts_root,
            "logs_bloom": self.logs_bloom,
        }



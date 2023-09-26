import rlp
from crypto import recover, sign
import json


class Transaction(rlp.Serializable):
    fields = [
        ("nonce", rlp.sedes.big_endian_int),
        ("gas_price", rlp.sedes.big_endian_int),
        ("gas", rlp.sedes.big_endian_int),
        ("to", rlp.sedes.binary),
        ("value", rlp.sedes.big_endian_int),
        ("data", rlp.sedes.binary),
        ("v", rlp.sedes.big_endian_int),
        ("r", rlp.sedes.big_endian_int),
        ("s", rlp.sedes.big_endian_int),
    ]

    def __init__(self, nonce, gas_price, gas, to, value, data, v=0, r=0, s=0):
        super(Transaction, self).__init__(
            nonce, gas_price, gas, to, value, data, v, r, s
        )

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self))

    @property
    def sender(self):
        return recover(self.hash, self.s)

    def sign(self, key):
        self.v, self.r, self.s = sign(self.hash, key)

    def to_dict(self):
        return {
            "nonce": self.nonce,
            "gasPrice": self.gas_price,
            "gas": self.gas,
            "to": self.to,
            "value": self.value,
            "data": self.data,
            "v": self.v,
            "r": self.r,
            "s": self.s,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            nonce=d["nonce"],
            gas_price=d["gasPrice"],
            gas=d["gas"],
            to=d["to"],
            value=d["value"],
            data=d["data"],
            v=d["v"],
            r=d["r"],
            s=d["s"],
        )

    def __repr__(self):
        return "<Transaction({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8})>".format(
            self.nonce,
            self.gas_price,
            self.gas,
            self.to,
            self.value,
            self.data,
            self.v,
            self.r,
            self.s,
        )

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_string(self):
        return rlp.encode(self).encode("hex")

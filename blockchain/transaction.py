import rlp
from crypto import recover, sign, sha3
from utils import exclude, check_values, decode_hex


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
        return sha3(rlp.encode(self))

    @property
    def sign_hash(self):
        return sha3(rlp.encode(exclude(self, ["v", "r", "s"])))

    @property
    def sender(self):
        return recover(self.hash, self.s)

    def sign(self, key):
        self.v, self.r, self.s = sign(self.hash, key)

    def validate(self):
        pass

    @property
    def is_valid(self):
        if (
            self.sender == self.to
            or not check_values(self)
            or not self.hash == sha3(rlp.encode(self))
        ):
            return False
        return True

    def __repr__(self):
        return (f"<Transaction #{self.nonce} sender={self.sender} to={self.to} value={self.value} gas={self.gas} "
                f"gas-price={self.gas_price})>")

    def encode_transaction(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode_transaction(cls, hex_transaction):
        return rlp.decode(decode_hex(hex_transaction), cls)

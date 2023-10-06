import rlp
from crypto import recover, sign, sha3
from utils import exclude, check_values, decode_hex


class Transaction(rlp.Serializable):
    fields = [
        ("gas_price", rlp.sedes.big_endian_int),
        ("gas", rlp.sedes.big_endian_int),
        ("to", rlp.sedes.binary),
        ("value", rlp.sedes.big_endian_int),
        ("data", rlp.sedes.binary),
        ("v", rlp.sedes.big_endian_int),
        ("r", rlp.sedes.big_endian_int),
        ("s", rlp.sedes.big_endian_int),
    ]

    def __init__(self, gas_price, gas, to, value, data, v=0, r=0, s=0):
        super(Transaction, self).__init__(
            gas_price, gas, to, value, data, v, r, s
        )

    @property
    def hash(self) -> bytes:
        return sha3(rlp.encode(self))

    @property
    def sign_hash(self) -> bytes:
        return sha3(rlp.encode(exclude(self, ["v", "r", "s"])))

    @property
    def sender(self) -> bytes:
        return recover(self.hash, self.s)

    def sign(self, key):
        self.__dict__["_v"], self.__dict__["_r"], self.__dict__["_s"] = sign(self.hash, key)

    @property
    def is_valid(self):
        if (
            self.sender == self.to
            | check_values(self)
            | self.check_nonce()
            # | check_balance()
            # | check_signature()
        ):
            return False
        return True

    def __repr__(self):
        return (f"<{self.__class__.__name__} sender=Test to={self.to} value={self.value} gas={self.gas} "
                f"gas-price={self.gas_price}>")

    @property
    def encode_transaction(self) -> str:
        return rlp.encode(self).hex()

    @classmethod
    def decode_transaction(cls, hex_transaction):
        return rlp.decode(decode_hex(hex_transaction), cls)

    def check_nonce(self):
        # acc = get_account(self.sender)
        # if acc.get_nonce() == self.nonce:
        #   return True
        # return False
        pass

    def check_balance(self):
        # check if sender have enough money
        # acc = get_account(self.sender)
        # if acc.solde(token) >= self.value:
        #   return True
        # return False
        pass

    def check_signature(self):
        # check if signature is valid
        pass

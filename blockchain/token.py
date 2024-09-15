import rlp
from kademlia.utils import decode_hex
from kademlia.crypto import sha3


class Token(rlp.Serializable):

    fields = [
        ("id", rlp.sedes.big_endian_int),
        ("name", rlp.sedes.binary),
        ("symbol", rlp.sedes.binary),
        ("total_supply", rlp.sedes.big_endian_int),
        ("balance", rlp.sedes.big_endian_int),
        ("allowances", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self, id=0, name="", symbol="", total_supply=0, balance=0, allowances=()):
        super(Token, self).__init__(id, name, symbol, total_supply, balance, allowances)
        pass

    def __repr__(self):
        return (f"<{self.__class__.__name__} name={self.name} symbol={self.symbol} totalSupply={self.total_supply} "
                f"balance={self.balance})>")

    def hash(self):
        return sha3(rlp.encode(self))

    def encode_token(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode_token(cls, hex_token):
        if isinstance(hex_token, bytes):
            return rlp.decode(decode_hex(hex_token.decode("utf-8")), cls)
        return rlp.decode(decode_hex(hex_token), cls)

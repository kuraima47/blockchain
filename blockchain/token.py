import rlp
from utils import decode_hex
from crypto import sha3


class Token(rlp.Serializable):

    fields = [
        ("name", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("symbol", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("decimals", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("totalSupply", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("balances", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("allowances", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self):
        super(Token, self).__init__()
        pass

    def __repr__(self):
        return (f"<Token name={self.name} symbol={self.symbol} decimals={self.decimals} totalSupply={self.totalSupply} "
                f"balances={self.balances})>")

    def hash(self):
        return sha3(rlp.encode(self))

    def encode_token(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode_token(cls, hex_token):
        return rlp.decode(decode_hex(hex_token), cls)

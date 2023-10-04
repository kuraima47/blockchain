import rlp
from utils import decode_hex


class Wallet(rlp.Serializable):

    fields = [
        ("addresse", rlp.sedes.binary),
        ("tokens", rlp.sedes.CountableList(rlp.sedes.binary))
    ]

    def __init__(self, addresse, tokens=[]):
        super(Wallet, self).__init__(addresse, tokens)

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_wallet):
        return rlp.decode(decode_hex(hex_wallet), cls)

    def get_token(self, index):
        if isinstance(self.tokens[index], bytes):
            return Token.decode(self.tokens[index].decode("utf-8"))
        return Token.decode(self.tokens[index])


class Token(rlp.Serializable):

    fields = [
        ("addresse", rlp.sedes.binary),
        ("solde", rlp.sedes.big_endian_int)
    ]

    def __init__(self):
        super(Token, self).__init__()

    def __repr__(self):
        return f"<Token addresse={self.addresse} montant={self.montant} >"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_token):
        return rlp.decode(decode_hex(hex_token), cls)

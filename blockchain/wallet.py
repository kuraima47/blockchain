import rlp
from utils import decode_hex
from crypto import sha3
import os


class Wallet(rlp.Serializable):

    fields = [
        ("addresse", rlp.sedes.binary),
        ("tokens", rlp.sedes.CountableList(rlp.sedes.binary))
    ]

    def __init__(self, addresse=b'', tokens=()):
        if addresse == b'':
            self.__dict__['_addresse'] = self.new
        super(Wallet, self).__init__(addresse, tokens)

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_wallet):
        return rlp.decode(decode_hex(hex_wallet), cls)

    def add_token(self, token) -> None:
        self.__dict__['_tokens'] += token.encode,

    def get_token(self, index):
        if isinstance(self.tokens[index], bytes):
            return Token.decode(self.tokens[index].decode("utf-8"))
        return Token.decode(self.tokens[index])

    @property
    def solde(self) -> float:
        return sum([self.get_token(i).solde for i in range(len(self.tokens))])

    @classmethod
    def new(cls):
        # Add Logic for create new wallet
        return cls(os.urandom(32))


class Token(rlp.Serializable):

    fields = [
        ("hash", rlp.sedes.binary),
        ("solde", rlp.sedes.big_endian_int)
    ]

    def __init__(self, hash, solde=0.0):
        super(Token, self).__init__(hash, solde)

    def __repr__(self):
        return f"<{self.__class__.__name__} addresse={self.addresse} montant={self.montant}>"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_token):
        return rlp.decode(decode_hex(hex_token), cls)

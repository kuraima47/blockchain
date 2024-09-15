import rlp
from kademlia.utils import decode_hex
from .Wallet.wallet import create_address


class Wallet(rlp.Serializable):

    fields = [
        ("address", rlp.sedes.binary),
        ("tokens", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("nonce", rlp.sedes.big_endian_int),
    ]

    def __init__(self, address=b'', tokens=(), nonce=0):
        if address == b'':
            self.__dict__['_address'] = self.new
        super(Wallet, self).__init__(address, tokens, nonce)

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_wallet):
        if isinstance(hex_wallet, bytes):
            return rlp.decode(decode_hex(hex_wallet.decode("utf-8")), cls)
        return rlp.decode(decode_hex(hex_wallet), cls)

    def add_token(self, token) -> None:
        self.__dict__['_tokens'] += token.encode,

    def get_token(self, index):
        if isinstance(self.tokens[index], bytes):
            return Token.decode(self.tokens[index].decode("utf-8"))
        return Token.decode(self.tokens[index])

    def get_address(self):
        return Address.decode(self.address)

    @property
    def solde(self) -> float:
        return sum([self.get_token(i).solde for i in range(len(self.tokens))])

    def solde(self, token) -> float:
        return self.get_token(token).solde

    @classmethod
    def new(cls):
        n_add = create_address()
        encoded_children = [Children(c["address"], c["xpublic_key"], c["path"], c["bip32_path"]).encode for c in n_add["children"]]
        address = Address(n_add["public_key"], n_add["private_key"], n_add["coin"], n_add["xpublic_key"], n_add["xprivate_key"], n_add["address"], n_add["wif"], encoded_children).encode
        return cls(address, [], 0)


class Token(rlp.Serializable):

    fields = [
        ("hash", rlp.sedes.binary),
        ("solde", rlp.sedes.big_endian_int)
    ]

    def __init__(self, hash, solde=0.0):
        super(Token, self).__init__(hash, solde)

    def __repr__(self):
        return f"<{self.__class__.__name__} hash={self.hash} solde={self.solde}>"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_token):
        if isinstance(hex_token, bytes):
            return rlp.decode(decode_hex(hex_token.decode("utf-8")), cls)
        return rlp.decode(decode_hex(hex_token), cls)


class Address(rlp.Serializable):

    fields = [
        ("public_key", rlp.sedes.binary),
        ("private_key", rlp.sedes.binary),
        ("coin", rlp.sedes.binary),
        ("xpublic_key", rlp.sedes.binary),
        ("xprivate_key", rlp.sedes.binary),
        ("address", rlp.sedes.binary),
        ("wif", rlp.sedes.binary),
        ("childrens", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self, public_key=b'', private=b'', coin=b'', xpublic_key=b'', xprivate='', address=b'', wif=b'', childrens=()):
        super(Address, self).__init__(public_key, private, coin, xpublic_key, xprivate, address, wif, childrens)

    def __repr__(self):
        return f"<{self.__class__.__name__} address={self.address} coin={self.coin}>"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_address):
        if isinstance(hex_address, bytes):
            return rlp.decode(decode_hex(hex_address.decode("utf-8")), cls)
        return rlp.decode(decode_hex(hex_address), cls)


class Children(rlp.Serializable):

    fields = [
        ("address", rlp.sedes.binary),
        ("xpublic_key", rlp.sedes.binary),
        ("path", rlp.sedes.binary),
        ("bip32_path", rlp.sedes.binary),
    ]

    def __init__(self, address=b'', xpublic_key=b'', path=b'', bip32_path=b''):
        super(Children, self).__init__(address, xpublic_key, path, bip32_path)

    def __repr__(self):
        return f"<{self.__class__.__name__} address={self.address} path={self.path}>"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_children):
        if isinstance(hex_children, bytes):
            return rlp.decode(decode_hex(hex_children.decode("utf-8")), cls)
        return rlp.decode(decode_hex(hex_children), cls)
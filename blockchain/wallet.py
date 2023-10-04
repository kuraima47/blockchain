import rlp


class Wallet(rlp.Serializable):

    fields = [
        ("addresse", rlp.sedes.binary),
        ("tokens", rlp.sedes.CountableList(rlp.sedes.binary))
    ]

    def __init__(self, name, symbol, decimals):
        super(Wallet, self).__init__(name, symbol, decimals)


class Token(rlp.Serializable):

    fields = [
        ("addresse", rlp.sedes.binary),
        ("montant", rlp.sedes.big_endian_int)
    ]

    def __init__(self):
        super(Token, self).__init__()

    @property
    def solde(self):
        return self.montant

import rlp


class Wallet(rlp.Serializable):

    fields = [
        ("name", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("symbol", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("decimals", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self, name, symbol, decimals):
        super(Wallet, self).__init__(name, symbol, decimals)

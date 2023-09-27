import rlp


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

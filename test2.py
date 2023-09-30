from rlp import Serializable, encode, decode
import rlp

class Transaction(Serializable):
    fields = [
        ('sender', rlp.sedes.binary),
        ('receiver', rlp.sedes.binary),
        ('value', rlp.sedes.big_endian_int),
    ]

    def __init__(self, sender, receiver, value):
        super(Transaction, self).__init__(sender, receiver, value)

tx = Transaction(sender='Alice', receiver='Bob', value=10)
encoded_tx = encode(tx)
decoded_tx = decode(encoded_tx, Transaction)
print(decoded_tx.sender)  # Affiche les données binaires

# Décoder le champ pour obtenir la valeur originale
original_sender = rlp.decode(decoded_tx.sender)[1:].decode('utf-8')
print(original_sender)  # Devrait afficher 'Alice'

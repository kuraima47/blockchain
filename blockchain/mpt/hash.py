
from crypto import sha3  # pysha3


def keccak_hash(data):
    return sha3(data)



from kademlia.crypto import sha3


def keccak_hash(data):
    return sha3(data)


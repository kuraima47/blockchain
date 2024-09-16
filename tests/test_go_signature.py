from kademlia.crypto import ecdsa_sign, mk_privkey, privtopub, ecdsa_recover, ECCx
from kademlia.utils import decode_hex
import rlp
from Crypto.Hash import keccak

def sha3(data):
    return keccak.new(digest_bits=256, data=data).digest()

def test_pyelliptic_sig():
    priv_seed = "test"
    priv_key = mk_privkey(priv_seed)
    my_pubkey = privtopub(priv_key)
    e = ECCx(raw_privkey=priv_key)
    msg = b"a"
    s = e.sign(msg)
    s2 = e.sign(msg)
    assert s != s2  # non déterministe

def test_go_sig():
    r_pubkey = decode_hex(
        "ab16b8c7fc1febb74ceedf1349944ffd4a04d11802451d02e808f08cb3b0c1c1"
        "a9c4e1efb7d309a762baa4c9c8da08890b3b712d1666b5b630d6c6a09cbba171"
    )
    d = {
        "signed_data": "a061e5b799b5bb3a3a68a7eab6ee11207d90672e796510ac455e985bd206e240",
        "cmd": "find_node",
        "body": (
            "03f847b840ab16b8c7fc1febb74ceedf1349944ffd4a04d11802451d02e808f0"
            "8cb3b0c1c1a9c4e1efb7d309a762baa4c9c8da08890b3b712d1666b5b630d6c6"
            "a09cbba1718454e869b1"
        ),
        "signature": (
            "0de032c62e30f4a9f9f07f25ac5377c5a531116147617a6c08f946c97991f351"
            "577e53ae138210bdb7447bab53f3398d746d42c64a9ce67a6248e59353f1bc6e"
            "01"
        ),
    }

    priv_seed = "test"
    priv_key = mk_privkey(priv_seed)
    expected_priv_key = decode_hex(
        "9c22ff5f21f0b81b113e63f7db6da94fedef11b2119b4088b89664fb9a3cb658"
    )
    assert priv_key == expected_priv_key
    my_pubkey = privtopub(priv_key)
    assert my_pubkey == r_pubkey, (my_pubkey, r_pubkey)
    go_body = decode_hex(d["body"])  # cmd_id, RLP encodé

    # Décoder le corps RLP
    decoded_body = rlp.decode(go_body[1:])
    target_node_id = decoded_body[0]
    expiry = decoded_body[1]
    assert target_node_id == r_pubkey  # recherche de lui-même
    go_signed_data = decode_hex(d["signed_data"])
    go_signature = decode_hex(d["signature"])

    my_signature = ecdsa_sign(go_signed_data, priv_key)
    assert my_signature == ecdsa_sign(go_signed_data, priv_key)  # k déterministe

    assert len(go_signed_data) == 32  # sha3()
    assert len(go_signature) == 65
    assert len(my_signature) == 65  # longueur correcte

    try:
        assert my_signature == go_signature
        failed = False
    except AssertionError:
        # Échec attendu, les signatures Go ne sont pas générées avec un k déterministe
        failed = True
    assert failed

    # Le décodage fonctionne lorsque nous avons signé
    recovered_pubkey = ecdsa_recover(go_signed_data, my_signature)
    assert my_pubkey == recovered_pubkey

    # Problème : nous ne pouvons pas décoder la clé publique à partir de la signature Go
    # et Go ne peut pas décoder la nôtre
    try:
        recovered_pubkey_from_go_sig = ecdsa_recover(go_signed_data, go_signature)
    except Exception as e:
        print("Impossible de récupérer la clé publique à partir de la signature Go :", e)

if __name__ == "__main__":
    test_pyelliptic_sig()
    test_go_sig()

import os

from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import (
    hashes,
    hmac,
    serialization,
)
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.concatkdf import ConcatKDFHash
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from coincurve import PublicKey
from Crypto.Hash import keccak

CIPHERNAMES = {"aes-128-ctr"}

sha3_256 = lambda x: keccak.new(digest_bits=256, data=str_to_bytes(x))
hmac_sha256 = lambda key, data: hmac.HMAC(key, data, sha256)


class ECIESDecryptionError(Exception):
    pass


class ECCx:
    """
    Classe modifiée pour fonctionner avec le format raw_pubkey utilisé dans RLPx
    et en liant la courbe et le cipher par défaut.
    """

    ecies_ciphername = "aes-128-ctr"
    curve = ec.SECP256K1()
    ecies_encrypt_overhead_length = 113

    def __init__(self, raw_pubkey=None, raw_privkey=None):
        backend = default_backend()
        if raw_privkey:
            self.private_key = ec.derive_private_key(
                int.from_bytes(raw_privkey, "big"), self.curve, backend
            )
            self.public_key = self.private_key.public_key()
        elif raw_pubkey:
            self.public_key = ec.EllipticCurvePublicKey.from_encoded_point(
                self.curve, b"\x04" + raw_pubkey
            )
            self.private_key = None
        else:
            self.private_key = ec.generate_private_key(self.curve, backend)
            self.public_key = self.private_key.public_key()

        self.raw_pubkey = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )[1:]  # Exclure le préfixe 0x04

        if self.private_key:
            self.raw_privkey = self.private_key.private_numbers().private_value.to_bytes(
                32, "big"
            )
        else:
            self.raw_privkey = None

    def get_ecdh_key(self, raw_pubkey):
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            self.curve, b"\x04" + raw_pubkey
        )
        shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)
        return shared_key

    @classmethod
    def ecies_encrypt(cls, data, raw_pubkey, shared_mac_data=b""):
        # Générer une clé éphémère
        backend = default_backend()
        ephem_private_key = ec.generate_private_key(cls.curve, backend)
        ephem_public_key = ephem_private_key.public_key()

        # Dériver la clé partagée
        peer_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            cls.curve, b"\x04" + raw_pubkey
        )
        shared_key = ephem_private_key.exchange(ec.ECDH(), peer_public_key)

        # Utiliser KDF pour dériver les clés de chiffrement et de MAC
        key_material = eciesKDF(shared_key, 32)
        key_enc, key_mac = key_material[:16], key_material[16:]

        # Chiffrer les données
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key_enc), modes.CTR(iv), backend=backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()

        # Calculer le tag HMAC
        h = hmac.HMAC(key_mac, hashes.SHA256(), backend=backend)
        h.update(ciphertext + shared_mac_data)
        tag = h.finalize()

        # Construire le message final
        ephem_pubkey_bytes = ephem_public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )[1:]  # Exclure le préfixe 0x04

        msg = b"\x04" + ephem_pubkey_bytes + iv + ciphertext + tag

        return msg

    def ecies_decrypt(self, data, shared_mac_data=b""):
        backend = default_backend()
        if data[:1] != b"\x04":
            raise ECIESDecryptionError("Invalid message header")

        # Extraire les composants du message
        ephem_pubkey_bytes = data[1:65]
        iv = data[65:81]
        ciphertext = data[81:-32]
        tag = data[-32:]

        # Reconstruire la clé publique éphémère
        ephem_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            self.curve, b"\x04" + ephem_pubkey_bytes
        )

        # Dériver la clé partagée
        shared_key = self.private_key.exchange(ec.ECDH(), ephem_public_key)

        # Utiliser KDF pour dériver les clés de chiffrement et de MAC
        key_material = eciesKDF(shared_key, 32)
        key_enc, key_mac = key_material[:16], key_material[16:]

        # Vérifier le tag HMAC
        h = hmac.HMAC(key_mac, hashes.SHA256(), backend=backend)
        h.update(ciphertext + shared_mac_data)
        try:
            h.verify(tag)
        except InvalidSignature:
            raise ECIESDecryptionError("Fail to verify data")

        # Déchiffrer les données
        cipher = Cipher(algorithms.AES(key_enc), modes.CTR(iv), backend=backend)
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext

    encrypt = ecies_encrypt
    decrypt = ecies_decrypt

    def sign(self, data):
        signature = ecdsa_sign(data, self.raw_privkey)
        return signature

    def verify(self, signature, message):
        return ecdsa_verify(self.raw_pubkey, signature, message)


def lzpad32(x):
    return b"\x00" * (32 - len(x)) + x


def _encode_sig(v, r, s):
    assert isinstance(v, int)
    assert v in (27, 28)
    vb, rb, sb = bytes([v - 27]), r.to_bytes(32, "big"), s.to_bytes(32, "big")
    return lzpad32(rb) + lzpad32(sb) + vb


def fvn(a, b, fnv_prime=0x01000193, offset_basis=0x811C9DC5):
    """
    Applique le hachage FNV-1a sur deux entiers combinés.

    :param a: Premier entier.
    :param b: Deuxième entier.
    :param fnv_prime: Constante FNV prime pour 32 bits.
    :param offset_basis: Biais initial FNV pour 32 bits.
    :return: Valeur de hachage FNV-1a en entier.
    """
    data = a.to_bytes(4, byteorder='big', signed=False) + b.to_bytes(4, byteorder='big', signed=False)

    hash_value = offset_basis
    for byte in data:
        hash_value ^= byte
        hash_value = (hash_value * fnv_prime) % (1 << 32)
    return hash_value


def fvnHash(int_mix, data, fnv_prime=0x01000193, offset_basis=0x811C9DC5):
    """
    Applique le hachage FNV-1a sur une combinaison de int_mix et data.

    :param int_mix: Liste d'entiers (par exemple, int_mix[i % 64]).
    :param data: Slice de cache sous forme de bytes.
    :param fnv_prime: Constante FNV prime pour 32 bits.
    :param offset_basis: Biais initial FNV pour 32 bits.
    :return: Valeur de hachage FNV-1a en entier.
    """
    # Convertir la liste d'entiers en bytes (4 octets par entier)
    int_mix_bytes = b''.join(i.to_bytes(4, byteorder='big', signed=False) for i in int_mix)

    # Combiner avec les données fournies
    combined_data = int_mix_bytes + bytes(data)

    hash_value = offset_basis
    for byte in combined_data:
        hash_value ^= byte
        hash_value = (hash_value * fnv_prime) % (1 << 32)  # Assure un résultat sur 32 bits
    return hash_value

def _decode_sig(sig):
    return (
        safe_ord(sig[64]) + 27,
        int.from_bytes(sig[0:32], "big"),
        int.from_bytes(sig[32:64], "big"),
    )


def ecdsa_verify(pubkey, signature, message):
    public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        ec.SECP256K1(), b"\x04" + pubkey
    )
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False


verify = ecdsa_verify


def ecdsa_sign(msghash, privkey):
    private_key = ec.derive_private_key(
        int.from_bytes(privkey, "big"), ec.SECP256K1(), default_backend()
    )
    signature = private_key.sign(msghash, ec.ECDSA(hashes.SHA256()))
    return signature


sign = ecdsa_sign


def ecdsa_recover(message, signature):
    assert len(signature) == 65
    pk = PublicKey.from_signature_and_message(signature, message, hasher=None)
    return pk.format(compressed=False)[1:]


recover = ecdsa_recover


def sha3(seed):
    return sha3_256(seed).digest()


def mk_privkey(seed):
    return sha3(seed)


def privtopub(raw_privkey):
    private_key = ec.derive_private_key(
        int.from_bytes(raw_privkey, "big"), ec.SECP256K1(), default_backend()
    )
    public_key = private_key.public_key()
    raw_pubkey = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )[1:]  # Exclure le préfixe 0x04
    return raw_pubkey


def encrypt(data, raw_pubkey):
    """
    Chiffre les données avec la méthode ECIES en utilisant la clé publique du destinataire.
    """
    assert len(raw_pubkey) == 64, "Invalid pubkey length: {}".format(len(raw_pubkey))
    return ECCx.ecies_encrypt(data, raw_pubkey)


def eciesKDF(shared_key, key_len):
    """
    NIST SP 800-56a Concatenation Key Derivation Function (voir section 5.8.1).
    """
    ckdf = ConcatKDFHash(
        algorithm=hashes.SHA256(),
        length=key_len,
        otherinfo=None,
        backend=default_backend(),
    )
    key_material = ckdf.derive(shared_key)
    return key_material

def str_to_bytes(s):
    if isinstance(s, str):
        return s.encode()
    elif isinstance(s, bytes):
        return s
    else:
        raise TypeError("Argument must be str or bytes, got {}".format(type(s)))

def bytes_to_str(b) -> str:
    if isinstance(b, bytes):
        return b.decode()
    elif isinstance(b, str):
        return b
    else:
        raise TypeError(f"Non géré : {type(b)}")
from __future__ import print_function
import struct
import rlp
import collections
import sys
import base64
import json
import argparse
import socket
from collections.abc import Mapping
from eth_utils import *
from hashlib import sha3_256

from blockchain.storage import Storage


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


def safe_ord(value):
    return value if isinstance(value, int) else ord(value)


def ascii_chr(i: int) -> bytes:
    return bytes([i])


ienc = int_to_big_endian = rlp.sedes.big_endian_int.serialize


def big_endian_to_int(s):
    return rlp.sedes.big_endian_int.deserialize(s.lstrip(b"\x00"))


idec = big_endian_to_int


def int_to_big_endian4(integer):
    """4 bytes big endian integer"""
    return struct.pack(">I", integer)


ienc4 = int_to_big_endian4

node_uri_scheme = "mychain://v1."


def host_port_pubkey_from_uri(uri):
    b_node_uri_scheme = str_to_bytes(node_uri_scheme)
    b_uri = str_to_bytes(uri)
    assert b_uri.startswith(b_node_uri_scheme), b_uri
    node_info = json.loads(
        base64.b64decode(bytes_to_str(uri)[len(node_uri_scheme):]).decode()
    )
    pubkey = decode_hex(node_info["pub_key"])
    assert len(pubkey) == 512 // 8
    return node_info["ip"], node_info["port"], pubkey


def host_port_pubkey_to_uri(host, port, pubkey):
    assert len(pubkey) == 512 // 8
    print(pubkey)
    uri = str_to_bytes(
        "{}{}".format(
            node_uri_scheme,
            base64.b64encode(
                json.dumps(
                    {
                        "pub_key": bytes_to_str(encode_hex(pubkey)),
                        "ip": host,
                        "port": port,
                    }
                ).encode()
            ).decode(),
        )
    )
    return uri


PY3 = sys.version_info[0] >= 3


def get_local_ip():
    return [
        ip
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]
        if ip.startswith("192.")
    ][0]


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ho", "--host", help="host ip address", type=str, default=None)
    parser.add_argument("-p", "--port", help="host port adress", type=str, default=None)
    parser.add_argument(
        "-n", "--nodes", help="link of existing node", type=str, default=None
    )
    return parser.parse_args()


def remove_chars(s, chars):
    if PY3:
        d = {safe_ord(c): None for c in chars}
        return s.translate(d)
    else:
        return s.translate(None, chars)


def hex_decode_config(self):
    def _with_dict(d):
        "recursively search and decode hex encoded data"
        for k, v in d.items():
            if k.endswith("_hex"):
                d[k[: -len("_hex")]] = decode_hex(v)
            if isinstance(v, dict):
                _with_dict(v)

    _with_dict(self.config)


def update_config_with_defaults(config, default_config):
    for k, v in default_config.items():
        if isinstance(v, Mapping):
            r = update_config_with_defaults(config.get(k, {}), v)
            config[k] = r
        elif k not in config:
            config[k] = default_config[k]
    return config


def exclude(d, keys):
    return [(k, v) for k, v in d if k not in keys]


# Check return false because no error, if return true one error is detected


def check_values(o):
    # return false because all values are not None
    for f in vars(o):
        if getattr(o, f) is None:
            return True
    return False


def check_nonce(sender, nonce):
    # return false because nonce is valid
    # check if nonce is valid
    # acc = get_account(self.sender)
    # if acc.get_nonce() > self.nonce:
    #   return True
    return False


def check_balance(sender, value, gas_price, type="standard"):
    # return false because sender have enough money
    # check if sender have enough money
    # acc = get_account(self.sender)
    # estimated_gas = 21000 if type == "standard" else 90000
    # if acc.solde(token) < self.value + estimated_gas * self.gas_price:
    #   return True
    return False


def check_signature(sender, hash, s):
    # return false because signature is valid
    # check if signature is valid
    # if self.sender != recover(self.hash, self.s):
    #   return True
    return False


def check_gas(gas, type="standard"):
    # return false because gas is valid
    # check if gas is valid
    # estimated_gas = 21000 if type == "standard" else 90000
    # if self.gas < estimated_gas:
    #   return True
    return False


def is_dict(d):
    for i in d:
        if not isinstance(i, list):
            return False
    return True


def parse(v):
    if isinstance(v, int) or isinstance(v, float) or isinstance(v, bool):
        return rlp.encode([bytes(v.__class__.__name__, "utf-8"), bytes(str(v), "utf-8")])
    elif isinstance(v, str):
        return rlp.encode([bytes(v.__class__.__name__, "utf-8"), bytes(v, "utf-8")])
    elif isinstance(v, tuple):
        return rlp.encode([bytes(v.__class__.__name__, "utf-8"),
                           bytes("(" + str(b','.join([parse(i) for i in v])) + ")", "utf-8")])
    elif isinstance(v, list):
        return rlp.encode([bytes(v.__class__.__name__, "utf-8"), [parse(i) for i in v]])
    elif isinstance(v, dict):
        return rlp.encode([bytes(v.__class__.__name__, "utf-8"),
                           [(bytes(k, "utf-8"), parse(i)) for k, i in v.items()]])
    else:
        return v


def unparse(v):
    try:
        v = rlp.decode(v)
    except: v = v
    if isinstance(v[0], bytes):
        v[0] = v[0].decode("utf-8")
    if isinstance(v[1], bytes):
        v[1] = v[1].decode("utf-8")
    cn, o = v
    if cn == "dict":
        return {k.decode("utf-8"): unparse(rlp.decode(i)) for k, i in o}
    elif cn == "bool":
        return True if o == "True" else False
    elif cn == "int":
        return int(o)
    elif cn == "float":
        return float(o)
    elif cn == "tuple":
        t = [unparse(i.encode('utf-8').decode('unicode_escape').encode('latin1')) for i in o[3:len(o) - 2].split(",")]
        return tuple(t)
    elif cn == "list":
        return [unparse(i) for i in o]
    else:
        try:
            return unparse(rlp.decode(bytes(o, "utf-8")))
        except:
            return o


def parse_data(obj):
    obj.data = [(bytes(k, "utf-8"), parse(getattr(obj, k))) for k in vars(obj) if "data" not in k]
    return rlp.encode(obj.data)


def unparse_data(obj, data):
    for i in rlp.decode(data):
        obj.__dict__[i[0].decode("utf-8")] = unparse(rlp.decode(i[1]))


def generate_contract_address(creator_address, creator_nonce):
    rlp_encoded = rlp.encode([creator_address, creator_nonce])
    contract_address = sha3_256(rlp_encoded).digest()[12:]  # Prendre les 20 derniers octets
    return contract_address


def get_function_selector(function_signature):
    # function_signature est une chaîne comme 'transfer(address,uint256)'
    keccak_hash = keccak(text=function_signature)
    return keccak_hash[:4]  # Les 4 premiers octets


def encode_uint256(value: int):
    return value.to_bytes(32, byteorder='big')


def encode_address(value):
    if isinstance(value, str):
        value = bytes.fromhex(value.replace('0x', ''))
    return value.rjust(32, b'\0')  # Padding à gauche pour atteindre 32 octets


def encode_bool(value):
    return (b'\x01' if value else b'\x00').rjust(32, b'\0')


def encode_abi(arg_types, args):
    if len(arg_types) != len(args):
        raise ValueError("Le nombre de types et d'arguments ne correspond pas.")

    encoded_args = b''
    for arg_type, arg in zip(arg_types, args):
        if arg_type == 'uint256':
            encoded_args += encode_uint256(arg)
        elif arg_type == 'address':
            encoded_args += encode_address(arg)
        elif arg_type == 'bool':
            encoded_args += encode_bool(arg)
        else:
            raise NotImplementedError(f"Type non supporté : {arg_type}")
    return encoded_args


def encode_function_call(function_name, arg_types, args):
    function_signature = f"{function_name}({','.join(arg_types)})"
    function_hash = keccak(function_signature.encode())
    function_selector = function_hash[:4]  # Les 4 premiers octets

    encoded_args = encode_abi(arg_types, args)

    return function_selector + encoded_args


def encode_function_call_no_args(function_name):
    function_signature = f"{function_name}()"
    function_hash = keccak(function_signature.encode())
    function_selector = function_hash[:4]
    return function_selector


def compute_transactions_root(transactions):
    thx_mpt = Storage(in_memory=True)
    for tx in transactions:
        thx_mpt[tx.hash] = rlp.encode
    return thx_mpt.current_root


def compute_receipts_root(receipts):
    receipts_mpt = Storage(in_memory=True)
    for receipt in receipts:
        receipts_mpt[receipt.transaction_hash] = rlp.encode(receipt)
    return receipts_mpt.current_root

# ###### colors ###############


COLOR_FAIL = "\033[91m"
COLOR_BOLD = "\033[1m"
COLOR_UNDERLINE = "\033[4m"
COLOR_END = "\033[0m"

colors = ["\033[9%dm" % i for i in range(0, 7)]
colors += ["\033[4%dm" % i for i in range(1, 8)]


def cstr(num, txt):
    return "%s%s%s" % (colors[num % len(colors)], txt, COLOR_END)


def cprint(num, txt):
    print(cstr(num, txt))


def phx(x):
    return encode_hex(x)[:8]


if __name__ == "__main__":
    for i in range(len(colors)):
        cprint(i, "test")

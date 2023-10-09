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
from blockchain.blockchain import handler
from eth_utils import *


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
    if isinstance(v, int):
        return bytes(str(v), "utf-8")
    elif isinstance(v, str):
        return bytes(v, "utf-8")
    elif isinstance(v, list):
        return rlp.encode([parse(i) for i in v])
    elif isinstance(v, dict):
        return rlp.encode([(bytes(k, "utf-8"), parse(i)) for k, i in v.items()])
    # else is when class is bytes
    else:
        return v


def unparse(v):
    if isinstance(v, bytes):
        s = v.decode("utf-8")
        if is_integer(s):
            return int(s)
        elif is_float(s):
            return float(s)
        else:
            return s
    elif is_dict(v):
        return {k.decode("utf-8"): unparse(i) for k, i in v}
    elif isinstance(v, list):
        return [unparse(i) for i in v]


def is_integer(n):
    if n.startswith("-"):
        n = n[1:]
    return n.isdigit()


def is_float(n):
    if n.startswith("-"):
        n = n[1:]
    return n.replace('.', '', 1).isdigit()


def parse_data(obj):
    obj.data = [(bytes(k, "utf-8"), parse(getattr(obj, k))) for k in vars(obj) if "data" not in k]
    obj.parsed_data = rlp.encode(obj.data)


def unparse_data(obj, data):
    for i in rlp.decode(data):
        obj.__dict__[i[0].decode("utf-8")] = unparse(rlp.decode(i[1]))

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

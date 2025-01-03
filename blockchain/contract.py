import rlp
from kademlia.utils import decode_hex, parse_data, unparse_data


class Contract(rlp.Serializable):

    fields = [
        ("hash", rlp.sedes.binary),
        ("code", rlp.sedes.binary),
        ("storage_hash", rlp.sedes.binary),
    ]

    def __init__(self, hash, code, storage_hash):
        # self.storage = Storage.decode(get_storage(storage_hash))
        """
        Usage : self.storage.key
        """
        super(Contract, self).__init__(hash, code, storage_hash)
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Storage(rlp.Serializable):

    fields = [
        ("hash", rlp.sedes.binary),
        ("data", rlp.sedes.CountableList(rlp.sedes.binary))
    ]

    def __init__(self, hash=b'', data=None):
        """
        data can take : list, dict, str, int, float, bytes, bool, None, tuple
        """
        if data is None:
            data = ""
        else:
            unparse_data(self, data)
        super(Storage, self).__init__(hash, data)

    def __repr__(self):
        return f"<{self.__class__.__name__} hash={self.hash} data={self.data}>"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_storage):
        if isinstance(hex_storage, bytes):
            return rlp.decode(decode_hex(hex_storage.decode('utf-8')), cls)
        return rlp.decode(decode_hex(hex_storage), cls)

    def parse(self):
        return parse_data(self)

    def unparse(self):
        return unparse_data(self, self.data)

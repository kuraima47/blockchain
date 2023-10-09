import rlp
from utils import decode_hex
# import lib of memory analysis


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
        super(Contract, self).__init__()
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

    def execute(self):
        # execute self.code
        pass


class Storage(rlp.Serializable):

    fields = [
        ("hash", rlp.sedes.binary),
        ("data", rlp.sedes.CountableList(rlp.sedes.binary))
    ]

    def __init__(self, hash=b'', data=None):
        """
        for the moment data is list of bytes [b'', b'', b'']
        """
        if data is None:
            data = [("hash", hash)]
        super(Storage, self).__init__(hash, data)
        for k, v in data:
            self.__dict__[k] = v

    def __repr__(self):
        return f"<{self.__class__.__name__} hash={self.hash} data={self.data}>"

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_storage):
        if isinstance(hex_storage, bytes):
            return rlp.decode(decode_hex(hex_storage.decode('utf-8')))
        return rlp.decode(decode_hex(hex_storage))

    def parser(self):
        for o in vars():
            print(o)

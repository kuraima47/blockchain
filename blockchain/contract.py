import rlp
from utils import decode_hex
# import lib of memory analysis


class Contract(rlp.Serializable):

    def __init__(self, hash, code, storage_hash):
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
        if data is None:
            data = [("hash", hash)]
        super(Storage, self).__init__(hash, data)

    def __repr__(self):
        return f"<{self.__class__.__name__} hash={self.hash} data={self.data}>"

    def get(self, key):
        return [v for k, v in self.data][0]

    def set(self, key, value):
        for k, v in self.data:
            if k == key:
                self.data.remove((k, v))
        self.data.append((key, value))

    @property
    def encode(self):
        return rlp.encode(self).hex()

    @classmethod
    def decode(cls, hex_storage):
        if isinstance(hex_storage, bytes):
            return rlp.decode(decode_hex(hex_storage.decode('utf-8')))
        return rlp.decode(decode_hex(hex_storage))

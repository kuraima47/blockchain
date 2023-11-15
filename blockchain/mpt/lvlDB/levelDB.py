from plyvel import *


class LevelDbStorage:

    def __init__(self, db_path):
        self.db = DB(db_path, create_if_missing=True)

    def __getitem__(self, item):
        value = self.db.get(item)
        if value is None:
            raise KeyError(f"Key not found : {item}")
        return value

    def __setitem__(self, key, value):
        self.db.put(key, value)

    def close(self):
        self.db.close()

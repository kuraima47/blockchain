import json
import os


class DBParser(dict):

    def __init__(self, on_dump=False):
        self.cache = {}
        self.on_dump = on_dump
        self.db_path = "./DB/"
        self.load()
        super().__init__()

    def __setitem__(self, key, value):
        super(DBParser, self).__setitem__(key, value)
        self.cache[key] = value
        if self.on_dump:
            self.dump()

    def load(self):
        for file in os.listdir(self.db_path):
            with open(self.db_path + file, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    self[k] = v
        else:
            pass

    def dump(self):
        for key, value in self.cache.items():
            with open(self.db_path + key + ".json", 'w') as f:
                json.dump({key: value}, f)

import rlp
from .storage import Storage
from .handler import Service


class State(Service):

    def __init__(self, name, storage_root=None):
        super().__init__()
        self.storage = Storage(storage_root)
        self.name = f"{self.__class__.__name__}_{name}"

    def get(self, key):
        return self.storage[key]

    def update(self, key, value):
        self.storage[key] = value

    def current_state_root(self):
        return self.storage.current_root

    def __repr__(self):
        return f"<{self.__class__.__name__} root={self.current_state_root()}>"

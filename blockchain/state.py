import rlp
from .storage import Storage
from .handler import Service


class State:

    def __init__(self, name, storage_root=None):
        self.storage = Storage(storage_root)
        self.name = f"{self.__class__.__name__}_{name}"

    def get(self, key):
        return self.storage[key]

    def update(self, key, value):
        self.storage[key] = value

    def current_state_root(self):
        return self.storage.current_root

    def copy(self):
        copy_obj = State(self.name, self.current_state_root())
        copy_obj.storage = self.storage.copy()
        return copy_obj

    def __repr__(self):
        return f"<{self.__class__.__name__} root={self.current_state_root()}>"


if __name__ == "__main__":
    global_state = State("global")
    contract_state = State("contract")
    adress_state = State("adress")
    global_state.update("contract_state", contract_state.current_state_root())
    global_state.update("adress_state", adress_state.current_state_root())

    #Récupéré les states
    new_contract_state = State("contract", global_state.get("contract_state"))
    new_adress_state = State("adress", global_state.get("adress_state"))

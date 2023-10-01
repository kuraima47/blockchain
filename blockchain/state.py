import rlp
from utils import decode_hex


class State(rlp.Serializable):

    fields = [
        ("eoa_accounts", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("accounts", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("contract_accounts", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("contract_storage", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("tx_pool", rlp.sedes.CountableList(rlp.sedes.binary)),
        ("blocks", rlp.sedes.CountableList(rlp.sedes.binary)),
    ]

    def __init__(self, eoa_accounts={}, accounts={}, contract_accounts={}, contract_storage={}, tx_pool=[], blocks=[]):
        super(State, self).__init__(
            eoa_accounts, accounts, contract_accounts, contract_storage, tx_pool, blocks
        )

    def get_account(self, address):
        return self.accounts[address]

    def get_eoa_account(self, address):
        return self.eoa_accounts[address]

    def get_contract_account(self, address):
        return self.contract_accounts[address]

    def get_contract_storage(self, address):
        return self.contract_storage[address]

    def get_tx_pool(self, address):
        return self.tx_pool[address]

    def get_block(self, address):
        return self.blocks[address]

    def add_account(self, account):
        if account in self.accounts:
            raise ValueError(f"Account {account.hash} already exists")
        self.accounts.append(account)

    def add_eoa_account(self, account):
        if account in self.accounts:
            raise ValueError(f"Account {account.hash} already exists")
        self.eoa_accounts.append(account)

    def add_contract_account(self, contract):
        if contract in self.contract_accounts:
            raise ValueError(f"Contract {contract.hash} already exists")
        self.contract_accounts.append(contract)

    def add_contract_storage(self, storage):
        if storage in self.contract_storage:
            raise ValueError(f"Storage {storage.hash} already exists")
        self.contract_storage.append(storage)

    def add_tx_pool(self, tx):
        if tx in self.tx_pool:
            raise ValueError(f"Transaction {tx.hash} already exists")
        self.tx_pool.append(tx)

    def add_block(self, block):
        self.blocks.append(block)

    def remove_tx_pool(self, tx):
        if tx not in self.tx_pool:
            raise ValueError(f"Transaction {tx.hash} does not exist")
        self.tx_pool.remove(tx)

    def transfer(self, sender, receiver, amount):
        if sender not in self.accounts | receiver not in self.accounts :
            raise ValueError("Either the sending or receiving account does not exist.")
        if self.accounts[sender] < amount:
            raise ValueError("Insufficient funds.")
        self.accounts[sender] -= amount
        self.accounts[receiver] += amount

    def encode_state(self) -> str:
        return rlp.encode(self).hex()

    @classmethod
    def decode_state(cls, hex_state):
        return rlp.decode(decode_hex(hex_state), cls)

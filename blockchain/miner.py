import threading
import queue
import time
import json

from blockchain.Consensus.Pow.consensus import ProofOfWork
from blockchain.VM.code import Code
from blockchain.block import Block, BlockHeader
from blockchain.VM.VM import VM
from blockchain.transaction import Transaction
from kademlia.utils import compute_transactions_root, compute_receipts_root


class Miner:
    def __init__(self, blockchain, txpool, wallet, handler):
        self.blockchain = blockchain
        self.txpool = txpool
        self.wallet = wallet
        self.handler = handler
        self.consensus_engine = ProofOfWork()
        self.mining = False

    def create_block_candidate(self):
        transactions = self.get_valid_transactions()
        parent_block = self.blockchain.get_latest_block()
        block_header = BlockHeader(
            number=parent_block.header.number + 1,
            parent_hash=parent_block.hash(),
            beneficiary=self.wallet.get_address(),
            difficulty=self.consensus_engine.calc_difficulty(
                self.blockchain, int(time.time()), parent_block.header
            ),
            timestamp=int(time.time()),
            gas_limit=1000000,
            gas_used=0,
            nonce='0' * 16,
            state_root=self.blockchain.state.current_state_root(),
            transaction_root=compute_transactions_root(transactions),
            receipts_root=compute_receipts_root([]),
            logs_bloom='',
            uncles_hash='',
            extra_data=''
        )
        block = Block(header=block_header, transactions=transactions)
        self.consensus_engine.prepare(self.blockchain, block.header)
        return block

    def get_valid_transactions(self):
        valid_transactions = []
        for tx in self.txpool:
            if self.validate_and_apply_transaction(tx):
                valid_transactions.append(tx)
            else:
                print(f"Transaction invalide ou échec de l'application: {tx}")
        return valid_transactions

    def validate_and_apply_transaction(self, tx: Transaction):
        if not tx.is_valid():
            print("Transaction invalide.")
            return False

        address_state_snapshot = self.blockchain.address_state.copy()
        contract_state_snapshot = self.blockchain.contract_state.copy()
        sender = tx.sender
        gas_price = tx.gas_price
        gas_limit = tx.gas

        sender_balance = address_state_snapshot.get(sender) or 0
        max_execution_cost = gas_price * gas_limit
        if sender_balance < max_execution_cost:
            print(
                f"Solde insuffisant pour l'adresse {sender}. Nécessaire: {max_execution_cost}, Disponible: {sender_balance}")
            return False
        gas_used = 0
        if tx.data:
            try:
                data_json = tx.data.decode('utf-8')
                transaction_data = json.loads(data_json)
            except (UnicodeDecodeError, json.JSONDecodeError) as e:
                print(f"Erreur lors du décodage des données de la transaction: {e}")
                return False

            action = transaction_data.get('action')
            if action == 'deploy_contract':
                contract_code = transaction_data.get('contract_code')
                if not contract_code:
                    print("Code du contrat manquant pour 'deploy_contract'.")
                    return False
                contract_address = self.generate_contract_address(sender, tx.nonce)
                contract_state_snapshot.update(contract_address, {
                    'code': contract_code,
                    'storage': {}
                })
                print(f"Contrat déployé à l'adresse {contract_address}.")
                code = Code(version=contract_code['version'], module=contract_code['module'], name=contract_code['name'], storage=b'')
                vm = VM(code=code, func='__init__', param=[])
                try:
                    vm.execute()
                    gas_used = vm.extractor.gas_used
                    vm_output = vm.get_output()
                    state_changes = self.extract_state_changes(vm_output)
                    self.apply_state_changes(address_state_snapshot, contract_state_snapshot, state_changes)
                except Exception as e:
                    print(f"Erreur lors de l'exécution initiale du contrat: {e}")
                    return False

            elif action == 'call_contract':
                contract_address = transaction_data.get('contract_address')
                func = transaction_data.get('function')
                params = transaction_data.get('parameters')
                if not contract_address or not func:
                    print("Adresse du contrat ou fonction manquante pour 'call_contract'.")
                    return False
                contract_state = contract_state_snapshot.get(contract_address)
                if not contract_state:
                    print(f"Contrat non trouvé à l'adresse {contract_address}.")
                    return False
                contract_code = contract_state.get('code')
                if not contract_code:
                    print(f"Code du contrat manquant pour l'adresse {contract_address}.")
                    return False
                code = Code(version=contract_code['version'], module=contract_code['module'], name=contract_code['name'], storage=contract_state['storage'])

                vm = VM(code=code, func=func, param=params)
                try:
                    vm.execute()
                    gas_used = vm.extractor.gas_used
                    vm_output = vm.get_output()
                    state_changes = self.extract_state_changes(vm_output)
                    self.apply_state_changes(address_state_snapshot, contract_state_snapshot, state_changes)
                except Exception as e:
                    print(f"Erreur lors de l'appel du contrat: {e}")
                    return False

            else:
                print(f"Action inconnue ou non autorisée: {action}")
                return False
        else:
            recipient = tx.to
            value = tx.value
            total_cost = value + (gas_price * gas_limit)
            if sender_balance < total_cost:
                print(
                    f"Solde insuffisant pour l'adresse {sender}. Nécessaire: {total_cost}, Disponible: {sender_balance}")
                return False

            sender_balance -= (value + gas_price * gas_limit)
            recipient_balance = address_state_snapshot.get(recipient) or 0
            recipient_balance += value
            address_state_snapshot.update(sender, sender_balance)
            address_state_snapshot.update(recipient, recipient_balance)

            gas_used = 21000

        execution_fee = gas_used * gas_price
        if sender_balance < execution_fee:
            print(
                f"Solde insuffisant pour les frais d'exécution pour l'adresse {sender}. Nécessaire: {execution_fee}, Disponible: {sender_balance}")
            return False
        sender_balance -= execution_fee
        address_state_snapshot.update(sender, sender_balance)

        self.blockchain.state.update('contract_state', contract_state_snapshot.current_state_root())
        self.blockchain.state.update('address_state', address_state_snapshot.current_state_root())
        self.blockchain.contract_state = contract_state_snapshot
        self.blockchain.address_state = address_state_snapshot
        return True

    def extract_state_changes(self, vm_output):
        state_changes = []
        for line in vm_output.split('\n'):
            if line.startswith('STATE_CHANGE:'):
                change_json = line[len('STATE_CHANGE:'):].strip()
                try:
                    change = json.loads(change_json)
                    state_changes.append(change)
                except json.JSONDecodeError as e:
                    print(f"Erreur lors du décodage du changement d'état: {e}")
        return state_changes

    def apply_state_changes(self, address_state_snapshot, contract_state_snapshot, state_changes):
        for change in state_changes:
            if change['type'] == 'address_state':
                address = change['address']
                balance_change = change['balance_change']
                current_balance = address_state_snapshot.get(address) or 0
                new_balance = current_balance + balance_change
                address_state_snapshot.update(address, new_balance)
            elif change['type'] == 'contract_state':
                contract_address = change['contract_address']
                storage_changes = change['storage_changes']
                contract_state = contract_state_snapshot.get(contract_address)
                if not contract_state:
                    print(
                        f"Contrat non trouvé à l'adresse {contract_address} lors de l'application des changements d'état.")
                    continue
                contract_storage = contract_state.get('storage', {})
                contract_storage.update(storage_changes)
                contract_state_snapshot.update(contract_address, {
                    'code': contract_state['code'],
                    'storage': contract_storage
                })
            else:
                print(f"Type de changement d'état inconnu: {change['type']}")

    def apply_changes_to_state(self, temp_address_changes, temp_contract_changes):
        for address, balance_change in temp_address_changes.items():
            current_balance = self.blockchain.address_state.get(address) or 0
            new_balance = current_balance + balance_change
            self.blockchain.address_state.update(address, new_balance)

        for contract_address, contract_data in temp_contract_changes.items():
            self.blockchain.contract_state.update(contract_address, contract_data)

    def generate_contract_address(self, sender_address, sender_nonce):
        import rlp
        from hashlib import sha3_256
        sender_bytes = bytes.fromhex(sender_address[2:])
        encoded = rlp.encode([sender_bytes, sender_nonce])
        contract_address = sha3_256(encoded).hexdigest()[24:]
        return '0x' + contract_address

    def mine_block(self, block):
        result_queue = queue.Queue()
        stop_event = threading.Event()

        mining_thread = threading.Thread(
            target=self.consensus_engine.seal,
            args=(self.blockchain, block, result_queue, stop_event)
        )
        mining_thread.start()

        while mining_thread.is_alive() and self.mining:
            try:
                mined_block = result_queue.get(timeout=1)
                if mined_block:
                    stop_event.set()
                    mining_thread.join()
                    return mined_block
            except queue.Empty:
                continue

        stop_event.set()
        mining_thread.join()
        return None

    def handle_mined_block(self, block):
        if self.blockchain.add_block(block):
            self.handler.broadcast_block(block)
            print("Bloc miné et ajouté à la blockchain !")
            self.clear_applied_transactions(block.transactions)
        else:
            print("Échec de l'ajout du bloc miné à la blockchain.")

    def clear_applied_transactions(self, transactions):
        for tx in transactions:
            if tx in self.txpool:
                self.txpool.remove(tx)

    def start_mining(self):
        self.mining = True
        while self.mining:
            latest_block = self.blockchain.get_latest_block()
            block_candidate = self.create_block_candidate()

            if not block_candidate.transactions:
                print("Aucune transaction valide à inclure, en attente...")
                time.sleep(5)
                continue

            mined_block = self.mine_block(block_candidate)
            if mined_block:
                self.handle_mined_block(mined_block)
            else:
                if self.blockchain.get_latest_block().hash() != latest_block.hash():
                    print("La blockchain a été mise à jour, redémarrage du minage.")
                    continue
                else:
                    print("Le minage a été interrompu.")
                    break

    def stop_mining(self):
        self.mining = False
        print("Arrêt du minage en cours...")


class Pool:
    def __init__(self):
        self.transactions = []

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def remove_transaction(self, transaction):
        self.transactions.remove(transaction)

    def get_transactions(self):
        return self.transactions

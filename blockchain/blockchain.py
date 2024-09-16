# blockchain.py

import sys
import time
import threading

from app import BaseApp
# Importations des modules nécessaires
from kademlia.service import WiredService
from kademlia.protocol import BaseProtocol
from kademlia.peermanager import PeerManager
from kademlia.discovery import NodeDiscovery
from kademlia.slogging import get_logger
from kademlia.utils import decode_hex, str_to_bytes, compute_transactions_root, compute_receipts_root

from blockchain.block import Block, BlockHeader
from blockchain.transaction import Transaction
from blockchain.state import State
from blockchain.miner import Miner
from blockchain.Consensus.Pow.consensus import ProofOfWork
from blockchain.Wallet.wallet import Wallet, create_wallet

# Importations supplémentaires
import rlp
import gevent

# Configuration du logger
log = get_logger('blockchain_app')

# Version de l'application
__version__ = '0.1'


class TransactionProtocol(BaseProtocol):
    protocol_id = 2
    network_id = 0
    max_cmd_id = 1
    name = b'transaction'
    version = 1

    def __init__(self, peer, service):
        self.config = peer.config
        super(TransactionProtocol, self).__init__(peer, service)

    class NewTransaction(BaseProtocol.command):
        cmd_id = 0
        structure = [
            ('transaction', Transaction)  # Transaction déjà sérialisée en RLP
        ]

    def send_new_transaction(self, transaction):
        cmd = self.NewTransaction(self.peer)
        # La transaction est déjà sérialisée en RLP
        rlp_transaction = rlp.encode(transaction)
        cmd.send(transaction=rlp_transaction)

    def receive_newtransaction(self, proto, transaction_rlp):
        # Décoder la transaction depuis RLP
        transaction = rlp.decode(transaction_rlp, Transaction)
        # Appeler la méthode handle_new_transaction de l'application
        self.service.app.handle_new_transaction(transaction)


class BlockProtocol(BaseProtocol):
    protocol_id = 3
    network_id = 0
    max_cmd_id = 1
    name = b'block'
    version = 1

    def __init__(self, peer, service):
        self.config = peer.config
        super(BlockProtocol, self).__init__(peer, service)

    class NewBlock(BaseProtocol.command):
        cmd_id = 0
        structure = [
            ('block', Block)  # Bloc déjà sérialisé en RLP
        ]

    def send_new_block(self, block):
        cmd = self.NewBlock(self.peer)
        # Le bloc est déjà sérialisé en RLP
        rlp_block = rlp.encode(block)
        cmd.send(block=rlp_block)

    def receive_newblock(self, proto, block_rlp):
        # Décoder le bloc depuis RLP
        block = rlp.decode(block_rlp, Block)
        # Appeler la méthode handle_new_block de l'application
        self.service.app.handle_new_block(block)


class BlockchainService(WiredService):
    # Nom du service
    name = 'blockchainservice'
    default_config = dict()

    # Protocoles pris en charge
    wire_protocols = [TransactionProtocol, BlockProtocol]

    def __init__(self, app):
        self.config = app.config
        self.address = app.wallet.get_address()
        super(BlockchainService, self).__init__(app)

    def on_wire_protocol_start(self, proto):
        if isinstance(proto, TransactionProtocol):
            proto.receive_newtransaction_callbacks.append(self.on_receive_new_transaction)
        elif isinstance(proto, BlockProtocol):
            proto.receive_newblock_callbacks.append(self.on_receive_new_block)

    def on_receive_new_transaction(self, proto, transaction_rlp):
        # Décoder la transaction depuis RLP
        transaction = rlp.decode(transaction_rlp, Transaction)
        self.app.handle_new_transaction(transaction)

    def on_receive_new_block(self, proto, block_rlp):
        # Décoder le bloc depuis RLP
        block = rlp.decode(block_rlp, Block)
        self.app.handle_new_block(block)

    def broadcast_transaction(self, transaction):
        log.debug('Diffusion de la transaction')
        for peer in self.app.services.peermanager.peers:
            proto = peer.protocols.get(b'transaction')
            if proto:
                proto.send_new_transaction(transaction)

    def broadcast_block(self, block):
        log.debug('Diffusion du bloc')
        for peer in self.app.services.peermanager.peers:
            proto = peer.protocols.get(b'block')
            if proto:
                proto.send_new_block(block)


class BlockchainApp(BaseApp):
    client_name = 'blockchainapp'
    version = '0.1'
    client_version = '%s/%s/%s' % (version, sys.platform,
                                   'py%d.%d.%d' % sys.version_info[:3])
    client_version_string = '%s/v%s' % (client_name, client_version)
    default_config = dict(BaseApp.default_config)
    default_config['client_version_string'] = client_version_string
    default_config['post_app_start_callback'] = None

    def __init__(self, config=None):
        super(BlockchainApp, self).__init__(config or self.default_config)
        self.state = State('global')
        self.chain = []
        self.txpool = []
        self.db_path = self.config.get('data_dir', './data')
        self.current_root = self.config.get('state_root', None)
        self.consensus_engine = None
        self.wallet = None
        self.miner = None
        self.running = False

    def start(self):
        self.setup()
        super(BlockchainApp, self).start()

        # Démarrer le mineur dans un thread séparé
        self.mining_thread = threading.Thread(target=self.miner.start_mining)
        self.mining_thread.start()

        log.info("Blockchain en cours d'exécution.")

    def stop(self):
        super(BlockchainApp, self).stop()
        # Arrêter le mineur
        self.miner.stop_mining()
        # Attendre la fin du thread de minage
        self.mining_thread.join()
        log.info("Blockchain arrêtée.")

    def setup(self):
        # Initialisation du stockage, état, consensus, portefeuille, mineur

        self.state = State('global', storage_root=self.current_root, db_path=self.db_path)

        # Initialiser les états des contrats et des adresses
        self.contract_state = State('contract', db_path=self.state.db_path)
        self.address_state = State('address', db_path=self.state.db_path)
        self.chain_state = State('chain', db_path=self.state.db_path)

        # Mettre à jour le global_state avec les racines des états
        self.state.update('contract_state', self.contract_state.current_state_root())
        self.state.update('address_state', self.address_state.current_state_root())
        self.state.update('chain_state', self.chain_state.current_state_root())
        self.consensus_engine = ProofOfWork()
        self.wallet = create_wallet()
        self.miner = Miner(
            blockchain=self,
            txpool=self.txpool,
            wallet=self.wallet,
            handler=self  # En l'absence d'un handler séparé, nous utilisons self
        )
        self.load_blockchain()

        # Enregistrer le service blockchain
        self.register_service(BlockchainService(self))

        # Enregistrer les services de découverte et de gestion des pairs
        NodeDiscovery.register_with_app(self)
        PeerManager.register_with_app(self)

    def load_blockchain(self):
        # Charger la blockchain depuis le stockage ou créer le bloc genesis
        if self.config.get('genesis_block'):
            genesis_block = self.config['genesis_block']
        else:
            genesis_block = self.create_genesis_block()

        # Récupérer les racines des états depuis le global_state
        contract_state_root = self.state.get('contract_state')
        address_state_root = self.state.get('address_state')
        chain_state_root = self.state.get('chain_state')

        # Recréer les états des contrats et des adresses
        self.contract_state = State('contract', storage_root=contract_state_root, db_path=self.state.db_path)
        self.address_state = State('address', storage_root=address_state_root, db_path=self.state.db_path)
        self.chain_state = State('chain', storage_root=chain_state_root, db_path=self.state.db_path)

        self.chain.append(genesis_block)
        self.chain_state.update(genesis_block.hash, genesis_block.encode_block)

        log.info("Blockchain initialisée avec le bloc genesis.")

    def create_genesis_block(self) -> Block:
        # Initialiser les états des contrats et des adresses vides
        self.contract_state = State('contract', db_path=self.state.db_path)
        self.address_state = State('address', db_path=self.state.db_path)
        self.chain_state = State('chain', db_path=self.state.db_path)
        # Mettre à jour le global_state avec les racines des états
        self.state.update('contract_state', self.contract_state.current_state_root())
        self.state.update('address_state', self.address_state.current_state_root())
        self.state.update('chain_state', self.chain_state.current_state_root())

        genesis_header = BlockHeader(
            number=0,
            parent_hash='0' * 64,
            beneficiary=self.wallet.get_address(),
            difficulty=1,
            timestamp=int(time.time()),
            gas_limit=10000000,
            gas_used=0,
            nonce='0' * 16,
            state_root=self.state.current_state_root(),
            transaction_root=compute_transactions_root([]),
            receipts_root=compute_receipts_root([]),
            logs_bloom='',
            uncles_hash='',
            extra_data='Genesis Block'
        )
        genesis_block = Block(header=genesis_header, transactions=[])
        return genesis_block

    def get_latest_block(self) -> Block:
        # Récupérer le dernier bloc de la chaîne
        return self.chain[-1]

    def add_block(self, block: Block) -> bool:
        # Ajouter un bloc à la chaîne après validation
        if self.validate_block(block):
            # Recréer les états des contrats et des adresses à partir du global_state
            self.chain_state = State('chain', storage_root=self.state.get('chain_state'), db_path=self.state.db_path)
            self.chain.append(block)
            self.chain_state.update(block.hash, block.encode_block)
            self.state.update('chain_state', self.chain_state.current_state_root())
            log.info(f"Bloc #{block.header.number} ajouté à la blockchain.")
            return True
        else:
            log.warning(f"Échec de la validation du bloc #{block.header.number}.")
            return False

    def validate_block(self, block: Block) -> bool:
        # Validation du bloc selon les règles du consensus
        parent_block = self.get_latest_block()
        try:
            self.consensus_engine.verify_header(self, block.header)
            if block.header.parent_hash != parent_block.hash:
                log.error("Le hash du parent ne correspond pas.")
                return False
            if block.header.number != parent_block.header.number + 1:
                log.error("Le numéro du bloc n'est pas séquentiel.")
                return False
            # Valider les transactions
            for tx in block.transactions:
                if not tx.is_valid():
                    log.error(f"Transaction invalide dans le bloc #{block.header.number}.")
                    return False
                else:
                    self.miner.validate_and_apply_transaction(tx)
            return True
        except Exception as e:
            log.error(f"Erreur lors de la validation du bloc: {e}")
            return False

    def handle_new_block(self, block: Block):
        # Gestion d'un nouveau bloc reçu depuis le réseau
        if self.add_block(block):
            # Si le bloc est valide et ajouté, diffuser aux autres nœuds
            self.broadcast_block(block)
            log.info(f"Bloc #{block.header.number} reçu et ajouté à la blockchain.")
        else:
            log.warning("Bloc reçu invalide ou déjà ajouté.")

    def handle_new_transaction(self, transaction: Transaction):
        # Gestion d'une nouvelle transaction reçue depuis le réseau
        self.new_transaction(transaction)

    def new_transaction(self, transaction: Transaction):
        # Ajouter une nouvelle transaction au pool
        if transaction.is_valid():
            self.txpool.append(transaction)
            # Diffuser la transaction aux pairs
            self.broadcast_transaction(transaction)
            log.info("Transaction ajoutée au pool et diffusée.")
        else:
            log.warning("Transaction invalide, rejetée.")

    def broadcast_block(self, block):
        blockchain_service = self.get_service(BlockchainService)
        if blockchain_service:
            blockchain_service.broadcast_block(block)
        else:
            log.error("BlockchainService non disponible pour diffuser le bloc.")

    def broadcast_transaction(self, transaction):
        blockchain_service = self.get_service(BlockchainService)
        if blockchain_service:
            blockchain_service.broadcast_transaction(transaction)
        else:
            log.error("BlockchainService non disponible pour diffuser la transaction.")

    def get_service(self, service_class):
        # Récupérer une instance d'un service enregistré en fonction de sa classe
        for service in self.services:
            if isinstance(service, service_class):
                return service
        return None


# Exemple d'utilisation
if __name__ == '__main__':
    # Configuration initiale (personnalisez selon vos besoins)
    config = {
        'network_id': 1,
        'data_dir': './data',
        'genesis_block': None,
        'client_version_string': 'blockchainapp/v0.1',
        'deactivated_services': [],
        'node': {
            'privkey_hex': '876dd25bdbc50845afcc85dd899c46f7810b5920da75a92d1184dc540b66c74c',
            'id': 'your_node_id_here'
        },
    }
    app = BlockchainApp(config)
    app.start()

    try:
        # Exécution principale
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Arrêt de l'application en cas d'interruption
        app.stop()
        app.join()
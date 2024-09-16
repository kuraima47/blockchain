from abc import ABC, abstractmethod
from typing import List
from blockchain.block import Block, BlockHeader
from blockchain.transaction import Transaction
import threading
import queue
import random
from concurrent.futures import ThreadPoolExecutor
import os


class ChainHeaderReader(ABC):

    @abstractmethod
    def config(self) -> dict:
        pass

    @abstractmethod
    def current_header(self) -> BlockHeader:
        pass

    @abstractmethod
    def get_header(self, hash: str, number: int) -> BlockHeader:
        pass

    @abstractmethod
    def get_header_by_number(self, number: int) -> BlockHeader:
        pass

    @abstractmethod
    def get_header_by_hash(self, hash: str) -> BlockHeader:
        pass

    @abstractmethod
    def get_td(self, hash: str, number: int) -> int:
        pass

class ConcreteChainHeaderReader(ChainHeaderReader):
    def __init__(self, blockchain_app):
        """
        Initialise le lecteur d'en-têtes de chaîne avec une instance de BlockchainApp.
        """
        self.blockchain_app = blockchain_app

    def config(self):
        """
        Retourne la configuration actuelle de la chaîne.
        """
        return {
            "network": "CustomBlockchain",
            "blockchain": "MyBlockchain",
            "version": self.blockchain_app.version,
            # Ajoutez d'autres configurations pertinentes si nécessaire
        }

    def current_header(self) -> BlockHeader:
        """
        Retourne l'en-tête du dernier bloc.
        """
        latest_block = self.blockchain_app.get_latest_block()
        if not latest_block:
            raise Exception("Aucun en-tête disponible")
        return latest_block.header

    def get_header(self, hash: str, number: int) -> BlockHeader:
        """
        Retourne un en-tête de bloc spécifique par hash et numéro.
        """
        block = self._find_block(hash, number)
        if block:
            return block.header
        raise ValueError(f"Aucun en-tête trouvé avec le hash {hash} et le numéro {number}")

    def get_header_by_number(self, number: int) -> BlockHeader:
        """
        Retourne un en-tête de bloc par numéro.
        """
        block = self._find_block_by_number(number)
        if block:
            return block.header
        raise ValueError(f"Aucun en-tête trouvé avec le numéro {number}")

    def get_header_by_hash(self, hash: str) -> BlockHeader:
        """
        Retourne un en-tête de bloc par hash.
        """
        block = self._find_block_by_hash(hash)
        if block:
            return block.header
        raise ValueError(f"Aucun en-tête trouvé avec le hash {hash}")

    def get_td(self, hash: str, number: int) -> int:
        """
        Retourne la difficulté totale (total difficulty) pour un bloc spécifique.
        """
        header = self.get_header(hash, number)
        return header.difficulty

    def _find_block(self, hash: str, number: int):
        """
        Recherche un bloc par hash et numéro.
        """
        for block in self.blockchain_app.chain:
            if block.hash.hex() == hash and block.header.number == number:
                return block
        return None

    def _find_block_by_number(self, number: int):
        """
        Recherche un bloc par numéro.
        """
        for block in self.blockchain_app.chain:
            if block.header.number == number:
                return block
        return None

    def _find_block_by_hash(self, hash: str):
        """
        Recherche un bloc par hash.
        """
        for block in self.blockchain_app.chain:
            if block.hash.hex() == hash:
                return block
        return None


class ChainReader(ABC):

    @abstractmethod
    def get_block(self, hash, number) -> Block:
        pass


class ConcreteChainReader(ChainReader):
    def __init__(self, blockchain_app):
        """
        Initialise le lecteur de chaîne avec une instance de BlockchainApp.
        """
        self.chainReaderHeader = ConcreteChainHeaderReader(blockchain_app)
        self.blockchain_app = blockchain_app

    def get_block(self, hash: str, number: int) -> Block:
        """
        Récupère un bloc spécifique par hash et numéro.
        """
        header = self.chainReaderHeader.get_header(hash, number)
        block = self._find_block(hash, number)
        if block:
            return block
        raise ValueError(f"Aucun bloc trouvé avec le hash {hash} et le numéro {number}")

    def _find_block(self, hash: str, number: int) -> Block:
        """
        Recherche un bloc dans la chaîne par hash et numéro.
        """
        for blk in self.blockchain_app.chain:
            if blk.hash.hex() == hash and blk.header.number == number:
                return blk
        return None

class Engine(ABC):

    @abstractmethod
    def author(self, header) -> tuple:
        pass

    @abstractmethod
    def verify_header(self, chain: ChainReader, header) -> bool:
        pass

    @abstractmethod
    def verify_headers(self, chain_header_reader, headers: List[BlockHeader]):
        pass

    @abstractmethod
    def verify_uncles(self, chain: ChainReader, block: Block) -> bool:
        pass

    @abstractmethod
    def prepare(self, chain: ChainReader, header: BlockHeader) -> bool:
        pass

    @abstractmethod
    def finalize(self, chain: ChainHeaderReader, header: BlockHeader, stateDB, txs: List[Transaction],
                 uncles: List[BlockHeader], withdrawals: List) -> None:
        pass

    @abstractmethod
    def finalize_and_assemble(self, chain: ChainHeaderReader, header: BlockHeader, stateDB, txs: List[Transaction],
                              uncles: List[BlockHeader], receipts: List, withdrawals: List) -> tuple:
        pass

    @abstractmethod
    def seal(self, chain: ChainHeaderReader, block: Block, results: queue.Queue, stop: threading.Event) -> bool:
        pass

    @abstractmethod
    def seal_hash(self, header: BlockHeader) -> str:
        pass

    @abstractmethod
    def calc_difficulty(self, chain: ChainHeaderReader, time: int, parent: BlockHeader) -> int:
        pass

    @abstractmethod
    def apis(self, chain: ChainHeaderReader) -> List:
        pass

    @abstractmethod
    def close(self) -> bool:
        pass


class PoW(ABC):

    engine: Engine

    def __init__(self, engine: Engine):
        self.engine = engine
        pass
    
    @abstractmethod
    def hash_rate(self) -> float:
        pass


from typing import Dict



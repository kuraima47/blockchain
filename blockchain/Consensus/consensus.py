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


class ChainReader(ABC):

    chainReaderHeader: ChainHeaderReader = ChainHeaderReader()

    @abstractmethod
    def get_block(self, hash, number) -> Block:
        pass


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
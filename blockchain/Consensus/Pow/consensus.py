import os
import random
from queue import Queue
import threading

import rlp
from repoze.lru import LRUCache

from blockchain.Consensus import *
import time

from blockchain.Consensus.Pow.dataset import Dataset
from crypto import sha3, fvn, fvnHash

params = {
    "DifficultyBoundDivisor": 2048,
    "MinimumDifficulty": 131072,
    "expDiffPeriod": 100000,
    "BlockReward": 5e+18,
    "MaximumExtraDataSize": 32,
    "allowedFutureBlockTimeSeconds": 15,
    "MaxGasLimit": 0x7fffffffffffffff,
    "MinGasLimit": 5000,
    "hashWords": 16,
    "mixBytes": 128,
    "loopAccesses": 64,
    "hashBytes": 64,
    "epochLength": 30000
}


class ProofOfWork(Engine):

    def __init__(self):
        self.fakeFull = False
        self.maxUncles = 2
        self.threads = 0
        self.rand = None
        self.lock = threading.Lock()
        self.update = threading.Event()
        self.caches = LRUCache(params["epochLength"])
        self.datasets = LRUCache(params["epochLength"])

    def author(self, header: BlockHeader) -> tuple:
        return header.beneficiary, None

    def verify_header(self, chain: ChainHeaderReader, header: BlockHeader) -> bool:
        number = header.number
        if chain.get_header(header.hash, number) is not None:
            return False
        parent = chain.get_header(header.parent_hash, number - 1)
        if parent is None:
            return False
        return verifyHeader(chain, header, parent, False, int(time.time()))

    def verify_headers(self, chain: ChainHeaderReader, headers: List[BlockHeader]) -> tuple:
        if self.fakeFull or len(headers) == 0:
            abort = Queue()
            results = Queue(maxsize=len(headers))
            for _ in headers:
                results.put(None)
            return abort, results
        abort = Queue()
        results = Queue(maxsize=len(headers))
        unixNow = int(time.time())

        def worker():
            for i, header in enumerate(headers):
                if i == 0:
                    parent = chain.get_header(header.parent_hash, header.number - 1)
                elif headers[i - 1].hash != header.parent_hash:
                    parent = headers[i - 1]

                error = None
                if parent is None:
                    error = f"parent not found: {header.parent_hash.hex()}"
                else:
                    error = verifyHeader(chain, header, parent, False, unixNow)

                if not abort.empty():
                    return
                results.put(error)

        threading.Thread(target=worker).start()
        return abort, results

    def verify_uncles(self, chain: ChainReader, block: Block) -> bool:
        if self.fakeFull:
            return True
        if len(block.uncles) > self.maxUncles:
            return False
        if len(block.uncles) > 0:
            return True

        uncles, ancestors = set(), {}
        number, parent = block.header.number, block.header.parent_hash

        for i in range(0, 7):
            ancestorHeader = chain.chainReaderHeader.get_header(parent, number)
            if ancestorHeader is None:
                break
            ancestors[parent] = ancestorHeader
            if ancestorHeader.uncle_hash != b'':
                ancestor = chain.get_block(parent, number)
                if ancestor is None:
                    break
                for _, uncle in enumerate(ancestor.uncles):
                    uncles.add(uncle.hash)
            parent, number = ancestorHeader.parent_hash, number - 1

        ancestors[block.hash] = block.header
        uncles.add(block.hash)
        for _, uncle in enumerate(block.uncles):
            hash = uncle.hash
            if uncles.__contains__(hash):
                return False
            uncles.add(hash)

            if ancestors[hash] is not None:
                return False
            if ancestors[uncle.parent_hash] is None or uncle.parent_hash != block.header.parent_hash:
                return False
            err = verifyHeader(chain.chainReaderHeader, uncle, ancestors[uncle.parent_hash], True, int(time.time()))
            if err is not None:
                return False
        return True

    def prepare(self, chain: ChainReader, header: BlockHeader) -> bool:
        parent = chain.chainReaderHeader.get_header(header.parent_hash, header.number - 1)
        if parent is None:
            return False
        return True

    def finalize(self, chain: ChainHeaderReader, header: BlockHeader, stateDB, txs: List[Transaction],
                 uncles: List[BlockHeader], withdrawals: List) -> None:
        accumulateRewards(chain.config(), stateDB, header, uncles)

    def finalize_and_assemble(self, chain: ChainHeaderReader, header: BlockHeader, stateDB, txs: List[Transaction],
                              uncles: List[BlockHeader], receipts: List, withdrawals: List) -> tuple:
        if len(withdrawals) > 0:
            return None, False

        self.finalize(chain, header, stateDB, txs, uncles, None)
        header.state_root = stateDB.root
        return Block(BlockHeader, txs), True

    def seal(self, chain: ChainHeaderReader, block: Block, results: queue.Queue, stop: threading.Event) -> bool:

        abort = threading.event()
        with self.lock:
            threads = self.threads
            if self.rand is None:
                seed = random.SystemRandom().randint(0, 2 ** 63 - 1)
                self.rand = random.Random(seed)

        if threads <= 0:
            threads = os.cpu_count()

        with ThreadPoolExecutor(max_workers=threads) as executor:

            local_blocks = queue.Queue()

            def miner_task(id, nonce):
                try:
                    if not abort.is_set():
                        mined_block = self.mine(block, id, nonce, abort)
                        if mined_block is not None:
                            local_blocks.put(mined_block)
                finally:
                    pass

            for i in range(threads):
                nonce = int(self.rand.random() * 2 ** 64)
                executor.submit(miner_task, i, nonce)

        while True:
            try:
                result = local_blocks.get(timeout=0.1)
                results.put(result)
                abort.set()
                break
            except queue.Empty:
                if stop.is_set():
                    abort.set()
                    break
                if self.update.is_set():
                    err = self.seal(chain, block, results, stop)
                    if not err:
                        print("error for restart sealing")

        executor.shutdown(wait=False)
        return True

    def seal_hash(self, header: BlockHeader) -> str:
        enc = rlp.encode([
            header.parent_hash,
            header.uncle_hash,
            header.coinbase,
            header.state_root,
            header.transaction_root,
            header.receipt_root,
            header.bloom,
            header.difficulty,
            header.number,
            header.gas_limit,
            header.gas_used,
            header.timestamp,
            header.extra_data
        ])
        return sha3(enc)

    def calc_difficulty(self, chain: ChainHeaderReader, time: int, parent: BlockHeader) -> int:
        return calcDifficulty(chain.config(), time, parent)

    def apis(self, chain: ChainHeaderReader) -> List:
        return ["eth", "net", "web3", "miner", "admin"]

    def close(self) -> bool:
        return True

    def mine(self, block: Block, id: int, seed: int, abort: threading.Event) -> tuple[Block, bytes]:
        header = block.header
        hash = self.seal_hash(header)
        target = 2 ** 256 // header.difficulty
        number = header.number
        dataset = self.dataset(number, False)

        attempts = 0
        nonce = seed

        print("Start Miner Thread : ", id)
        while True:
            if abort.is_set():
                print("Nonce search is aborted")
                break
            else:
                attempts += 1
                if (attempts % (1 << 15)) == 0:
                    # hashrate.mark(attempts)
                    # TODO Need To Implement hashrate marker
                    print("Hashrate", attempts)
                    attempts = 0

                digest, result = hashimotoFull(dataset, hash, nonce)
                if result <= target:
                    print("Ethash nonce found and reported", "attempts", nonce - seed, "nonce", nonce)
                    header.nonce = nonce
                    header.mix_hash = digest
                    return block, dataset
                nonce += 1

    def dataset(self, number: int, is_async: bool) -> bytes:
        epoch = number // params["epochLength"]
        current: Dataset = self.datasets.get(epoch)

        if is_async and not current.generated():
            def func():
                current.generate(dir="", limit=0, lock=False, test=False)

            threading.Thread(target=func).start()
        else:
            current.generate(dir="", limit=0, lock=False, test=False)

        return current.dataset


def verifyHeader(chain: ChainHeaderReader, header: BlockHeader, parent: BlockHeader, uncle: bool, now: int) -> bool:
    if len(header.extra_data) > params["MaximumExtraDataSize"]:
        return False

    if uncle is None:
        if header.timestamp > (now + params["allowedFutureBlockTimeSeconds"]):
            return False

    if header.timestamp <= parent.timestamp:
        return False

    excepted = calcDifficulty(chain.config(), header.timestamp, parent)

    if header.difficulty != excepted:
        return False

    if header.gas_limit > params["MaxGasLimit"]:
        return False

    if header.gas_used > header.gas_limit:
        return False

    if (header.number - parent.number) != 1:
        return False

    return True


def calcDifficulty(config: dict, time: int, parent: BlockHeader) -> int:
    nextConfig = parent.number + 1
    match config.get(nextConfig):
        case 0:
            return 0
        case _:
            return calcDifficultyFrontier(time, parent)


def calcDifficultyFrontier(time: int, parent: BlockHeader) -> int:
    adjust = parent.header.difficulty // params["DifficultyBoundDivisor"]
    big_time = time
    big_parent = parent.header.timestamp

    if big_time - big_parent < 13:
        diff = parent.header.difficulty + adjust
    else:
        diff = parent.header.difficulty - adjust

    if diff < params["MinimumDifficulty"]:
        return params["MinimumDifficulty"]

    period_count = (parent.header.number + 1) // params["expDiffPeriod"]
    if period_count > 1:
        exp_diff = 2 ** (period_count - 2)
        diff += exp_diff
        diff = max(diff, params["MinimumDifficulty"])
    return diff


def accumulateRewards(config, stateDB, header, uncles):
    blockReward = params["BlockReward"]
    reward = blockReward
    r = 0
    hNum = header.number

    for _, uncle in enumerate(uncles):
        uNum = uncles[_].number
        r = uNum + 8
        r -= hNum
        r *= blockReward
        r //= 8
        stateDB.add_balance(uncle.beneficiary, r)
        r //= 32
        reward += r
    stateDB.add_balance(header.beneficiary, reward)


def hashimotoFull(dataset: bytes, hash: bytes, nonce: int) -> tuple[bytes, bytes]:
    def lookup(index) -> [int]:
        offset = index * params["hashWords"]
        return dataset[offset:offset + params["hashWords"]]

    return hashimoto(hash, nonce, len(dataset) * 4, lookup)


def hashimoto(hash: bytes, nonce: int, size: int, lookup) -> tuple[bytes, bytes]:
    rows = size // params["mixBytes"]

    seed = hash
    seed += nonce.to_bytes(8, "little")
    seed = sha3(seed)
    seedHead = seed.to_bytes(32, "little")

    mix = []
    for i in len(params["mixBytes"] / 4):
        mix.append(seed[i % 16 * 4:].to_bytes(32, "little"))

    temp = []
    for i in range(params["loopAccesses"]):
        p = fvn(i ^ seedHead, mix[i % len(mix)]) % rows
        for j in range(params["mixBytes"] // params["hashBytes"]):
            temp[j * params["hashWords"]:] = lookup(2 * p + j)
        mix = fvnHash(mix, temp)

    for i in range(len(mix)):
        mix[i // 4] = fvn(fvn(fvn(mix[i], mix[i + 1]), mix[i + 2]), mix[i + 3])
    mix = mix[:len(mix) // 4]
    digest = []

    for i, val in enumerate(mix):
        digest[i * 4] = val.to_bytes(32, "little")

    return bytes(digest), sha3(seed + digest)

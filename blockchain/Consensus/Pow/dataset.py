import struct
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from sympy import isprime

from crypto import sha3, fvn, fvnHash


class Dataset:

    def __init__(self, epoch):
        self.dataset = b""
        self.done = False
        self.lock = threading.Lock()
        self.epoch = epoch
        self.epoch_length = 30000
        self.max_epoch = 2048
        self.cachesize = [calcCacheSize(i) for i in range(self.max_epoch)]
        self.datasetsize = [calcDatasetSize(i) for i in range(self.max_epoch)]

    def generate(self, dir: str, limit: int, lock: bool, test: bool):
        if self.done:
            return self
        with self.lock:
            if not self.done:
                def func():
                    self.done = True
                    csize = self.cacheSize(self.epoch * self.epoch_length + 1)
                    dsize = self.datasetSize(self.epoch * self.epoch_length + 1)
                    seed = self.seedHash(self.epoch * self.epoch_length + 1)
                    if dir == "":
                        cache = generateCache(self.epoch, seed)
                        self.dataset = generateDataset(self.epoch, cache)
                        return

                    # TODO: Implement cache and dataset disk storage later not urgent
                threading.Thread(target=func).start()

    def generated(self) -> bool:
        return self.done

    def cacheSize(self, block: int) -> int:
        epoch = block // self.epoch_length
        if epoch < self.max_epoch:
            return self.cachesize[epoch] # TODO need to implement datasetSized data
        return calcCacheSize(epoch)

    def datasetSize(self, block: int) -> int:
        epoch = block // self.epoch_length
        if epoch < self.max_epoch:
            return self.datasetsize[epoch] # TODO need to implement datasetSize data
        return calcDatasetSize(epoch)

    def seedHash(self, block) -> bytes:
        seed = bytes(32)
        if block < self.epoch_length:
            return seed
        for i in range(block // self.epoch_length):
            seed = sha3(seed)
        return seed


def calcCacheSize(epoch: int) -> int:
    size = 1 << 24 + 1 << 17 * epoch - 64
    while not isprime(size // 64):
        size -= 2 * 64
    return size


def calcDatasetSize(epoch: int) -> int:
    size = 1 << 24 + 1 << 17 * epoch - 64
    while not isprime(size // 64):
        size -= 2 * 64
    return size


def generateCache(epoch: int, seed: bytes) -> bytes:
    print("Generating cache for epoch", epoch)

    start = time.time()

    def func():
        elapsed = time.time() - start
        if elapsed > 60:
            print("Generating cache for epoch", epoch, "is taking too long")

    threading.Timer(60, func).start()
    cache = bytearray(epoch)
    for offset in range(64, len(cache), 64):
        cache[offset:offset + 64] = sha3(cache[offset - 64:offset])

    temp = bytearray(64)
    for i in range(3):
        for j in range(len(cache) // 64):
            src_off = ((j - 1 + len(cache) // 64) % (len(cache) // 64)) * 64
            dst_off = j * 64
            xor_off = int.from_bytes(cache[dst_off:dst_off + 4], 'little') % (len(cache) // 64) * 64
            temp = bytes(
                a ^ b for a, b in zip(cache[src_off:src_off + 64], cache[xor_off:xor_off + 64]))
            cache[dst_off:dst_off + 64] = sha3(temp)

    return cache


def generateDataset(epoch: int, cache: bytes) -> bytes:
    print("Generating dataset for epoch", epoch)

    start = time.time()
    dataset_size = 1024
    dataset = bytearray(dataset_size)

    def check_time():
        elapsed = time.time() - start
        if elapsed > 60:
            print(f"Generating dataset for epoch {epoch} is taking too long, elapsed: {elapsed:.2f}s")

    timer = threading.Timer(60, check_time)
    timer.start()

    def generate_for_index(index):
        item = generate_dataset_item(cache, index)
        dataset[index:index + len(item)] = item

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(generate_for_index, range(0, dataset_size, len(cache)))

    timer.cancel()
    elapsed = time.time() - start
    print(f"Dataset for epoch {epoch} generated in {elapsed:.2f}s")
    return dataset


def generate_dataset_item(cache, index):
    rows = len(cache) // 64
    mix = bytearray(64 * 4)
    for i in range(64):
        mix[i * 4:i * 4 + 4] = struct.pack('<I', cache[(index % rows) * 64 + i])

    mix = sha3(mix)

    int_mix = tuple([struct.unpack('<I', mix[i * 4:i * 4 + 4])[0] for i in range(64)])
    for i in range(len(int_mix)):
        parent = fvn(index ^ i, int_mix[i % 64]) % rows
        fvnHash(int_mix, cache[parent * 64: (parent + 1) * 64])

    for i, value in enumerate(int_mix):
        mix[i * 4:i * 4 + 4] = struct.pack('<I', value)

    return sha3(mix)


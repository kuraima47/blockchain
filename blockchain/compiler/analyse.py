import json
from collections import Counter


class Analyser:

    def __init__(self, version):
        self.bytesCodes = BytesCodes().get_bytecodes(version)

    def analyse(self, logs):
        opcode_counts = Counter()
        for line in logs.split("\n"):
            if line.startswith("*    "):
                opcode = line.split("(")[1].split(")")[0]
                opcode_counts.update(opcode)
        return sum(self.bytesCodes[opcode] * count for opcode, count in opcode_counts.items() if opcode in self.bytesCodes.keys())


class BytesCodes:

    def __init__(self):
        self.bytesCodes = {"3.12": {"LOAD_CONST": 1, "LOAD_FAST": 2, "CALL_FUNCTION": 3, "RETURN_VALUE": 4}}

    def get_bytecodes(self, version):
        return self.bytesCodes.get(version)
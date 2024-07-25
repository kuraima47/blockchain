from .bytescodes import BytesCodes


class Extractor:

    def __init__(self, version):
        self.gas = 21000
        self.bytesCodes = BytesCodes().get_bytecodes(version)

    def extract(self, logs):
        return self.gas + sum(self.__opcode_to_gas(self.__log_to_opcode(log)) for log in logs.split("\n"))

    def __log_to_opcode(self, log) -> str:
        if log.startswith("*Infos"):
            opcode = log.split("(")[1].split(")")[0]
            return opcode
        else:
            return None

    def __opcode_to_gas(self, opcode) -> int:
        if opcode is None:
            return 0
        try:
            return self.bytesCodes[opcode]
        except KeyError:
            return 1

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

class Extractor:

    def __init__(self):
        self.gas = 21000

    def extract(self, logs):
        for log in logs:
            self.gas += self.__opcode_to_gas(self.__log_to_opcode(log))

    def __log_to_opcode(self, log) -> str:
        pass

    def __opcode_to_gas(self, opcode) -> int:
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
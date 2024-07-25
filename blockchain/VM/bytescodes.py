import json


class BytesCodes:

    def __init__(self):
        self.bytesCodes = {"3.9": {"LOAD_CONST": 1, "LOAD_FAST": 2, "CALL_FUNCTION": 3, "RETURN_VALUE": 4}}

    def get_bytecodes(self, version):
        return self.bytesCodes[version]
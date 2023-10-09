import rlp
from utils import parse_data, unparse_data


class A:

    def __init__(self):
        self.data = []
        self.parsed_data = b''
        pass


a = A()
b = A()
a.__dict__["new"] = {"name": "coucou"}
a.__dict__["new_test"] = [1, 2, 3]
print(a.__dict__)
parse_data(a)
print(a.parsed_data)
print(b.__dict__)
unparse_data(b, a.parsed_data)
print(b.__dict__)


import rlp
from utils import parse_data, unparse_data


class A:

    def __init__(self):
        self.data = []


a = A()
b = A()
a.__dict__["new"] = {"name": "coucou"}
a.__dict__["new_test"] = [1, 2, 3]
print(a.__dict__)
unparse_data(b, parse_data(a))
print(b.__dict__)


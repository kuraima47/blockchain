from utils import parse_data, unparse_data


class A:
    def __init__(self):
        t = (1, 2, 3)
        self.a = {"a": t, "b": ["2R", 3, 5], "c": True, "d": False}


a = A()
print(vars(a))
data = parse_data(a)
b = A()
unparse_data(b, data)
print(vars(b))

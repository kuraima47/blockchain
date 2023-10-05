import os

rb = os.urandom(8)
rb2 = os.urandom(8)
print(f"rb : {rb}, rb2 : {rb2}")
print(rb < rb2)
print(rb[::-1].hex())
print(rb2[::-1].hex())
print(rb[::-1].hex() > rb2[::-1].hex())

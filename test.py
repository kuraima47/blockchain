from blockchain.handler import Service
import blockchain.blockchain as blockchain


class A(Service):
    def __init__(self):
        super().__init__()


obj = A()
assert isinstance(obj, Service), "obj is not a Service"
blockchain.handler.register_service(obj)
print("Service in handler:")
for service in blockchain.handler.services:
    print(" Service :", blockchain.handler.services[service].name)

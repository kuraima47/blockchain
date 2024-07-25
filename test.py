from blockchain.handler import Service
import blockchain.blockchain as blockchain


class A(Service):
    def __init__(self):
        super().__init__()
        self.handler = blockchain.handler
        assert isinstance(self, Service), "obj is not a Service"
        blockchain.handler.register_service(self)
        print("Service in handler:")
        for service in blockchain.handler.services:
            print(" Service :", blockchain.handler.services[service].name)

    def afficherService(self):
        print("Service in handler:")
        for service in blockchain.handler.services:
            print(" Service :", blockchain.handler.services[service].name)

service = A()
service.handler.services[service.name].afficherService()
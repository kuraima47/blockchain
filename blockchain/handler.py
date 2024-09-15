from app import BaseApp
from kademlia.service import BaseService

try:
    from UserDict import IterableUserDict
except ImportError:
    from collections import UserDict as IterableUserDict


class Handler:

    def __init__(self, services=[], config={}):
        super().__init__(config)
        self.services = IterableUserDict()
        for service in services:
            self.register_service(service)

    def register_service(self, service):
        assert isinstance(service, Service)
        assert service.name not in self.services
        print("registering service", service.name)
        self.services[service.name] = service
        setattr(self.services, service.name, service)

    def deregister_service(self, service):
        assert isinstance(service, Service)
        self.services.pop(service)
        delattr(self.services, service.name)

    def broadcast_transaction(self, transaction):
        pass

    def broadcast_block(self, block):
        pass

    def handle_new_block(self, block):
        if self.blockchain.add_block(block):
            pass


class Service(BaseService):

    def __init__(self, app):
        super().__init__(app)
        self.sub_service = IterableUserDict()
        self.name = self.__class__.__name__

    def init_sub_service(self, service=[]):
        for s in service:
            self.register_service(s)

    def register_service(self, service):
        assert isinstance(service, Service)
        assert service.name not in self.sub_service
        print("registering service", service.name)
        service.register_with_app(self.app)
        self.sub_service[service.name] = service
        setattr(self.sub_service, service.name, service)

    def deregister_service(self, service):
        assert isinstance(service, Service)
        self.sub_service.pop(service)
        delattr(self.sub_service, service.name)

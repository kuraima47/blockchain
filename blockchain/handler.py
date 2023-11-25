try:
    from UserDict import IterableUserDict
except ImportError:
    from collections import UserDict as IterableUserDict


class Handler:

    def __init__(self, services=[]):
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


class Service:

    def __init__(self):
        self.sub_service = IterableUserDict()
        self.name = self.__class__.__name__

    def init_sub_service(self, service=[]):
        for s in service:
            self.register_service(s)

    def register_service(self, service):
        assert isinstance(service, Service)
        assert service.name not in self.sub_service
        print("registering service", service.name)
        self.sub_service[service.name] = service
        setattr(self.sub_service, service.name, service)

    def deregister_service(self, service):
        assert isinstance(service, Service)
        self.sub_service.pop(service)
        delattr(self.sub_service, service.name)

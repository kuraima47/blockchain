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
        self.services.remove(service)
        delattr(self.services, service.name)


class Service:

    def __init__(self):
        self.name = self.__class__.__name__


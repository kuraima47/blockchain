try:
    from UserDict import IterableUserDict
except ImportError:
    from collections import UserDict as IterableUserDict
from kademlia.service import BaseService
from kademlia.slogging import get_logger
from kademlia import utils
from kademlia.utils import str_to_bytes

__version__ = "0.0.1"

log = get_logger("app")


class BaseApp(object):
    default_config = dict(
        client_version_string=str_to_bytes("pydevp2p {}".format(__version__)),
        deactivated_services=[],
    )

    def __init__(self, config=default_config):
        self.config = utils.update_config_with_defaults(config, self.default_config)
        self.services = IterableUserDict()

    def register_service(self, service):
        """
        registers protocol with app, which will be accessible as
        app.services.<protocol.name> (e.g. app.services.p2p or app.services.eth)
        """
        assert isinstance(service, BaseService)
        assert service.name not in self.services
        log.info("registering service", service=service.name)
        self.services[service.name] = service
        setattr(self.services, service.name, service)

    def deregister_service(self, service):
        assert isinstance(service, BaseService)
        self.services.remove(service)
        delattr(self.services, service.name)

    def start(self):
        for service in self.services.values():
            service.start()

    def stop(self):
        for service in self.services.values():
            service.stop()

    def join(self):
        for service in self.services.values():
            service.join()



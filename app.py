try:
    from UserDict import IterableUserDict
except ImportError:
    from collections import UserDict as IterableUserDict
from kademlia.service import BaseService
from kademlia.slogging import get_logger
from kademlia import crypto, utils, slogging
from kademlia.utils import decode_hex, parse_arguments, get_local_ip, str_to_bytes

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


def main():
    # config
    import yaml
    import io
    import sys
    import signal
    import gevent
    from gevent.event import Event
    from kademlia.peermanager import PeerManager
    from kademlia.discovery import NodeDiscovery

    slogging.basicConfig()
    log = slogging.get_logger("app")
    slogging.configure(config_string=":debug")
    log.setLevel(slogging.logging.DEBUG)
    args = parse_arguments()
    nl = "\n        "
    # read config
    sample_config = f"""
discovery:
    num_peers: 10
    bootstrap_nodes:
        # local bootstrap (omis pour le premier fullNode)
        # - mychain://v1.[base64_encoded_data_here]
        # go_bootstrap (omis pour le premier fullNode)
        # - mychain://v1.[base64_encoded_data_here]
        # cpp_bootstrap (omis pour le premier fullNode)
        # mychain://v1.eyJwdWJfa2V5IjogIjRhNDQ1OTk5NzQ1MThlYTViMGYxNGMzMWM0NDYzNjkyYWMwMzI5Y2I4NDg1MWYzNDM1ZTZkMWIxOGVlNGVhZTRhYTQ5NWY4NDZhMGZhMTIxOWJkNTgwMzU2NzE4ODFkNDQ0MjM4NzZlNTdkYjJhYmQ1NzI1NGQwMTk3ZGEwZWJlIiwgImlwIjogIjUuMS44My4yMjYiLCAicG9ydCI6ICIzMDMwMyJ9
        {nl.join(args.nodes.split(",")) if args.nodes else "#--nodes"}
    listen_host: {args.host if args.host else get_local_ip()}
    listen_port: {args.port if args.port else "30303"}
node:
    privkey_hex: 876dd25bdbc50845afcc85dd899c46f7810b5920da75a92d1184dc540b66c74c
p2p:
    min_peers: 5
    max_peers: 10
    listen_port: {args.port if args.port else "30303"}
    listen_host: {args.host if args.host else get_local_ip()}
    bootstrap_nodes:
        {nl.join(args.nodes.split(",")) if args.nodes else "#--nodes"}
    """
    if args is None:
        fn = sys.argv[1]
        log.info("loading config from", fn=fn)
        config = yaml.load(open(fn), Loader=yaml.SafeLoader)
    else:
        config = yaml.load(
            io.BytesIO(bytes(sample_config, "utf-8")), Loader=yaml.SafeLoader
        )
        pubkey = crypto.privtopub(decode_hex(config["node"]["privkey_hex"]))
        config["node"]["id"] = crypto.sha3(pubkey)

    # stop on every unhandled exception!
    gevent.get_hub().SYSTEM_ERROR = (
        BaseException  # (KeyboardInterrupt, SystemExit, SystemError)
    )
    # create app
    app = BaseApp(config)

    # register services
    NodeDiscovery.register_with_app(app)
    PeerManager.register_with_app(app)

    # start app
    app.start()

    # wait for interupt
    evt = Event()
    # gevent.signal(signal.SIGQUIT, gevent.kill) ## killall pattern
    gevent.signal_handler(signal.SIGINT, evt.set)
    gevent.signal_handler(signal.SIGTERM, evt.set)
    gevent.signal_handler(signal.SIGABRT, evt.set)
    evt.wait()

    # finally stop
    app.stop()


if __name__ == "__main__":
    #  python app.py 2>&1 | less +F
    main()

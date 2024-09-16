from eth_utils import decode_hex

from blockchain.blockchain import BlockchainApp
from kademlia import slogging, crypto
import yaml
import io
import sys
import signal
import gevent
from gevent.event import Event
from kademlia.peermanager import PeerManager
from kademlia.discovery import NodeDiscovery
from kademlia.utils import parse_arguments, get_local_ip


def main():
    # config
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
    app = BlockchainApp(config)

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

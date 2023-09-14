import slogging
from upnpy import UPnP

log = slogging.get_logger("p2p.upnp")

_upnp = None


def _init_upnp():
    global _upnp
    if _upnp:
        return _upnp
    try:
        log.debug("Discovering devices...")
        upnp = UPnP()
        upnp.discover()
        _upnp = upnp
    except Exception as e:
        log.debug("Exception :%s", e)
    finally:
        return _upnp


def add_portmap(port, proto, label=""):
    u = _init_upnp()
    try:
        device = u.get_igd()
        device.get_services()
        service = device["WANPPPConnection.1"]
        external_ip = service.GetExternalIPAddress()
        log.debug("External IP Address: %s", external_ip)
        service.AddPortMapping(
            NewRemoteHost="",
            NewExternalPort=port,
            NewProtocol=proto,
            NewInternalPort=port,
            NewInternalClient=external_ip,
            NewEnabled=1,
            NewPortMappingDescription=label,
            NewLeaseDuration=0,
        )
    except Exception as e:
        log.debug("Exception :%s", e)


def remove_portmap(port, proto):
    u = _init_upnp()
    if not u:
        return
    try:
        device = u.get_igd()
        device.get_services()
        service = device["WANPPPConnection.1"]
        service.DeletePortMapping(port, proto)
        log.debug("Successfully deleted port mapping")
    except Exception as e:
        log.debug("Exception :%s", e)

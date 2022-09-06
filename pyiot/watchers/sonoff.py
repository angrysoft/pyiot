from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import json
from threading import Event
from pyiot.watchers import WatcherBaseDriver


class EwelinkWatcher(WatcherBaseDriver):
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_ewelink._tcp.local.", self)
        self._loop = True
        self._handler = None
        self.ev = Event()

    def watch(self, handler):
        self._handler = handler
        self.ev.wait()
        self.zeroconf.close()

    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        pass

    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        # info = zeroconf.get_service_info(type, name)
        pass

    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        info = zeroconf.get_service_info(service_type, name)
        if self._handler is not None:
            self._handler(self._parse(info.properties))

    def _parse(self, prop):
        ret = {}
        if b"data1" in prop:
            _data = json.loads(prop[b"data1"])
            if "switch" in _data:
                _data["power"] = _data.pop("switch")
            ret = {
                "cmd": "report",
                "sid": prop[b"id"].decode(),
                "model": prop[b"type"].decode(),
                "data": _data,
            }
        return ret

    def stop(self):
        self.ev.set()

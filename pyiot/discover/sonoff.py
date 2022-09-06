from . import BaseDiscovery
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser
from threading import Event
import socket
import json
from typing import List, Dict, Any


class DiscoverSonoff(BaseDiscovery):
    def __init__(self) -> None:
        self.timeout = 10
        self.searching: Event = Event()
        self._devices_list: List[Dict[str, Any]] = []
        self._device: Dict[str, Any] = {}
        self._sid = "_NotSet_"

    def _find(self):
        zeroconf = Zeroconf()
        self.searching.clear()
        ServiceBrowser(zeroconf, "_ewelink._tcp.local.", self)
        self.searching.wait(self.timeout)
        zeroconf.close()

    def find_all(self) -> List[Dict[str, Any]]:
        self._devices_list.clear()
        self._sid = "_NotSet_"
        self._find()
        return self._devices_list

    def find_by_sid(self, sid: str) -> Dict[str, Any]:
        self._device.clear()
        self._sid = sid
        self._find()
        return self._device

    def remove_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        print(f"Service {name} removed")

    def update_service(self, zeroconf: Zeroconf, service_type: str, name: str):
        print(f"Service {name} updated")

    def add_service(self, zeroconf: Zeroconf, service_type: str, name: str) -> None:
        info: Dict[str, Any] = self._parse(
            zeroconf.get_service_info(service_type, name)
        )
        if info:
            if self._sid == info["id"]:
                self._device = info
                self.searching.set()
            else:
                self._devices_list.append(info)

    def _parse(self, info: ServiceInfo) -> Dict[str, Any]:
        ret: Dict[str, Any] = {}
        props: Dict[bytes, Any] = info.properties
        if b"data1" in props:
            try:
                ret = {
                    "id": props[b"id"].decode(),
                    "model": props[b"type"].decode(),
                    "ip": socket.inet_ntoa(info.addresses[0]),
                    "port": info.port,
                }
                ret.update(json.loads(props[b"data1"]))
            except IndexError:
                pass
        return ret

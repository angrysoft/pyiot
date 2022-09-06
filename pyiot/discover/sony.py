from . import BaseDiscovery
from pyiot.connections.udp import UdpConnection
from pyiot.exceptions import DeviceTimeout
from urllib.parse import urlparse
from uuid import UUID
from typing import List, Dict, Any


class DiscoverSony(BaseDiscovery):
    def __init__(self) -> None:
        self.ip: str = "239.255.255.250"
        self.port: int = 1900
        self.search_request: bytes = (
            "M-SEARCH * HTTP/1.1\r\n"
            "HOST: 239.255.255.250:1900\r\n"
            'MAN: "ssdp:discover"\r\n'
            "MX: 1\r\n"
            "ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n"
            "\r\n".encode()
        )

        self.conn = UdpConnection()
        self.conn.sock.settimeout(10)

    def find_all(self) -> List[Dict[str, Any]]:
        """Discover devices

        Args:
            timeout (int): socket timeout"""
        ret: List[Dict[str, Any]] = []

        self.conn.send(self.search_request, (self.ip, self.port))

        while True:
            try:
                data, addr = self.conn.recv(retry=0)
            except OSError:
                break
            except DeviceTimeout:
                break
            if data:
                dev = self._parse_devices(data.decode())
                if dev:
                    ret.append(dev)

        return ret

    def find_by_sid(self, sid: str) -> Dict[str, Any]:

        self.conn.send(self.search_request, (self.ip, self.port))
        while True:
            try:
                data, addr = self.conn.recv(retry=0)
            except OSError:
                break
            except DeviceTimeout:
                break
            if data:
                dev = self._parse_devices(data.decode())
                if dev and sid == dev["sid"]:
                    return dev
        return {}

    def _parse_devices(self, data_in: str) -> Dict[str, Any]:
        dev: Dict[str, Any] = {}
        for line in data_in.split("\r\n"):
            tmp = line.split(":", 1)
            if len(tmp) > 1:
                key, val = tmp
                key = key.lower()
                if (
                    key.startswith("cache-control")
                    or key.startswith("date")
                    or key.startswith("ext")
                ):
                    continue
                val = val.strip()
                if key == "support":
                    val = val.split(" ")
                elif key == "location":
                    print(val)
                    url = urlparse(val)
                    dev["ip"] = url.hostname
                    dev["port"] = url.port
                elif key == "usn":
                    try:
                        dev["sid"] = val.split(":")[1]
                    except IndexError:
                        pass
                else:
                    dev[key] = val
        return dev

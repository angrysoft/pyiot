from . import BaseDiscovery
from pyiot.connections.udp import UdpMulticastConnection
from pyiot.exceptions import DeviceTimeout
from urllib.parse import urlparse
from typing import List, Dict, Any


class DiscoverYeelight(BaseDiscovery):
    def __init__(self) -> None:
        self.ip: str = '239.255.255.250'
        self.port: int = 1982
        self.search_request: bytes = 'M-SEARCH * HTTP/1.1\r\n' \
                                     'HOST: 239.255.255.250:1982\r\n' \
                                     'MAN: "ssdp:discover"\r\n' \
                                     'ST: wifi_bulb\r\n'.encode()
                                     
        self.conn = UdpMulticastConnection()
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
                if dev and sid == dev['id']:
                    return dev
        return {}
    
    def _parse_devices(self, data_in:str) -> Dict[str, Any]:
        dev: Dict[str, Any] = {}
        for line in data_in.split('\r\n'):
            tmp = line.split(':', 1)
            if len(tmp) > 1:
                key, val = tmp
                key = key.lower()
                if key.startswith('cache-control') or key.startswith('date') or key.startswith('ext'):
                    continue
                val = val.strip()
                if key == 'support':
                    val = val.split(' ')
                elif key == 'location':
                    url = urlparse(val)
                    dev['ip'] = url.hostname
                    dev['port'] = url.port
                elif key in ('rgb', 'hue', 'sat'):
                    dev[key] = int(val)
                else:
                    dev[key] = val
                    
        return dev
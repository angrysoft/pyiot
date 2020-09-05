from abc import ABC, abstractmethod
from pyiot.exceptions import DeviceTimeout
from typing import Any, Dict, List
from pyiot.connections.udp import UdpBroadcastConnection, UdpMulticastConnection
from pyiot.xiaomi.protocol import MiioPacket
from urllib.parse import urlparse
import socket


class Discovery:
    engines = []
    
    def __init__(self):
        pass
  
class BaseDiscovery(ABC):
    @abstractmethod
    def find_all(self) -> List[Dict[str,Any]]:
        pass
    
    @abstractmethod
    def find_by_sid(self, sid:str) -> Dict[str,Any]:
        pass  

class DiscoverySonoff(BaseDiscovery):
    pass

class DiscoverySony(BaseDiscovery):
    pass

class DiscoveryYeelight(BaseDiscovery):
    def __init__(self) -> None:
        self.ip: str = '239.255.255.250'
        self.port: int = 1982
        self.search_request: bytes = 'M-SEARCH * HTTP/1.1\r\n' \
                                     'HOST: 239.255.255.250:1982\r\n' \
                                     'MAN: "ssdp:discover"\r\n' \
                                     'ST: wifi_bulb\r\n'.encode()
                                     
    def find_all(self) -> List[Dict[str, Any]]:
        """Discover devices
        
        Args:
            timeout (int): socket timeout"""
        ret: List[Dict[str, Any]] = []
        
        conn = UdpMulticastConnection()
        conn.sock.settimeout(10)
        conn.send(self.search_request, (self.ip, self.port))
        
        while True:
            try:
                data, addr = conn.recv(retry=0)
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
        return {}
    
    def _parse_devices(self, data_in:str) -> Dict[str, Any]:
        dev: Dict[str, Any] = {}
        for line in data_in.split('\r\n'):
            tmp = line.split(':', 1)
            print(tmp)
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
                    continue
                dev[key] = val
        return dev

class DiscoveryAqara(BaseDiscovery):
    pass

class DiscoveryMiio(BaseDiscovery):
    def __init__(self) -> None:
        self.conn = UdpBroadcastConnection()
        self.addr = "<broadcast>"
        self.port = 54321
        self.hellobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )
        
    def find_all(self) -> List[Dict[str, Any]]:
        """Scan for devices in the network.
        This method is used to discover supported devices by sending a
        handshake message to the broadcast address on port 54321.
        """
        ret: List[Dict[str, Any]] = []
        self.conn.send(self.hellobytes, (self.addr, self.port))
        while True:
            try:
                data, addr  = self.conn.recv(retry=0)
                head = MiioPacket.parse_head(data)
                ip, port = addr
                ret.append(dict(ip=ip, port=port, header=head))
            except socket.timeout:
                break
            except Exception as ex:
                break
        return ret
    
    
    def find_by_sid(self, sid: str) -> Dict[str, Any]:
        """Scan for devices in the network.
        This method is used to discover supported devices by sending a
        handshake message to the broadcast address on port 54321.
        """
        ret: Dict[str, Any] = {}
        self.conn.send(self.hellobytes, (self.addr, self.port))
    
        while True:
            try:
                data, addr  = self.conn.recv()
                head = MiioPacket.parse_head(data)
                if str(head['device_id']) == sid:
                    ip, port = addr
                    ret = dict(ip=ip, port=port, header=head)
                    break
            except socket.timeout:
                break
            except Exception as ex:
                break
        return ret

# Discover.engines.append(DiscoverySonoff())

# if __name__ == "__main__":
#     d = Discover()
#     print(d.engines)
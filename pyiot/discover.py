from abc import ABC, abstractmethod
from threading import Event
from pyiot.exceptions import DeviceTimeout
from typing import Any, Dict, List
from pyiot.connections.udp import UdpBroadcastConnection, UdpMulticastConnection, UdpConnection
from pyiot.xiaomi.protocol import MiioPacket
from urllib.parse import urlparse
import socket
import json
from zeroconf import ServiceInfo, Zeroconf, ServiceStateChange, ServiceBrowser


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
    def __init__(self) -> None:
        self.timeout = 10
        self.searching:Event = Event()
        self._devices_list: List[Dict[str, Any]] = []
        self._device: Dict[str, Any] = {}
        self._sid = '_NotSet_'
        
    def _find(self):
        zeroconf = Zeroconf()
        self.searching.clear()
        ServiceBrowser(zeroconf, "_ewelink._tcp.local.", handlers=[self._add_service])
        self.searching.wait(self.timeout)
        zeroconf.close()
            
    def find_all(self) -> List[Dict[str, Any]]:
        self._devices_list.clear()
        self._sid = '_NotSet_'
        self._find()
        return self._devices_list
    
    def find_by_sid(self, sid: str) -> Dict[str, Any]:
        self._device.clear()
        self._sid = sid
        self._find()
        return self._device
    
    def _add_service(self, zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
         if state_change is ServiceStateChange.Added:
            info:Dict[str,Any] = self._parse(zeroconf.get_service_info(service_type, name))
            if info:
                if self._sid == info['id']: 
                    self._device = info
                    self.searching.set()
                else:
                    self._devices_list.append(info)

    def _parse(self, info: ServiceInfo) -> Dict[str, Any]:
        ret:Dict[str,Any] = {}
        props:Dict[bytes, Any] = info.properties
        if b'data1' in props:
            try:
                ret = {'id': props[b'id'].decode(), 'model': props[b'type'].decode(),
                       'ip': socket.inet_ntoa(info.addresses[0]), 'port': info.port}
                ret.update(json.loads(props[b'data1']))
            except IndexError:
                pass
        return ret

class DiscoverySony(BaseDiscovery):
    def __init__(self) -> None:
        self.ip: str = '239.255.255.250'
        self.port: int = 1900
        self.search_request: bytes = 'M-SEARCH * HTTP/1.1\r\n' \
                                     'HOST: 239.255.255.250:1900\r\n' \
                                     'MAN: "ssdp:discover"\r\n' \
                                     'MX: 1\r\n' \
                                     'ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n' \
                                     '\r\n'.encode()
                                     
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
                    continue
                   
                dev[key] = val
        return dev

class DiscoveryYeelight(BaseDiscovery):
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
            except Exception:
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
            except Exception:
                break
        return ret

# Discover.engines.append(DiscoverySonoff())

# if __name__ == "__main__":
#     d = Discover()
#     print(d.engines)
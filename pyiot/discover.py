from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pyiot.connections.udp import UdpBroadcastConnection
from pyiot.xiaomi.protocol import MiioPacket
import socket


class Discovery:
    engines = []
    
    def __init__(self):
        pass
  
class BaseDiscovery(ABC):
    @abstractmethod
    def find_all(self) -> List[Dict[str,Any]]:
        pass
    
    def find_by_sid(self, sid:str) -> Dict[str,Any]:
        pass  

class DiscoverySonoff(BaseDiscovery):
    pass

class DiscoverySony(BaseDiscovery):
    pass

class DiscoveryYeelight(BaseDiscovery):
    pass

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
                data, addr  = self.conn.recv()
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
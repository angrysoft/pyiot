
from . import BaseDiscovery
from pyiot.connections.miio import MiioPacket
from pyiot.connections.udp import UdpBroadcastConnection
import socket
from typing import List, Dict, Any


class DiscoverMiio(BaseDiscovery):
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
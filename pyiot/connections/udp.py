import socket
from typing import Tuple, Any, Dict
import json
from pyiot.exceptions import DeviceIsOffline

class UdpConnection:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.settimeout(10)
        self._multicast_ip:str = ''
        self._multicast_port:int = 0
        self._unicast_ip:str = ''
        self._unicast_port:int = 0
    
    @property
    def multicast_ip(self) -> str:
        return self._multicast_ip
    
    @multicast_ip.setter
    def multicast_ip(self, value:str):
        self._multicast_ip = value
    
    @property
    def multicast_port(self) -> int:
        return self._multicast_port
    
    @multicast_port.setter
    def multicast_port(self, value:int):
        self._multicast_port = value
    
    @property
    def multicast_addr(self) -> Tuple[str,int]:
        if not self.multicast_ip:
            raise ValueError('Ip addr is not set')
        elif self.multicast_port == 0:
            raise ValueError('port is not set')
        return (self.multicast_ip, self.multicast_port)
    
    @property
    def unicast_ip(self) -> str:
        return self._unicast_ip
    
    @unicast_ip.setter
    def unicast_ip(self, value:str):
        self._unicast_ip = value
    
    @property
    def unicast_port(self) -> int:
        return self._unicast_port
    
    @unicast_port.setter
    def unicast_port(self, value:int):
        self._unicast_port = value
    
    @property
    def unicast_addr(self) ->Tuple[str,int]:
        if not self.unicast_ip:
            raise ValueError('Ip addr is not set')
        elif self.unicast_port == 0:
            raise ValueError('port is not set')
        return (self.unicast_ip, self.unicast_port)
    
    def send_multicast(self, **kwargs:Any) -> Dict[str,Any]:
        try:
            return self.send(kwargs, self.multicast_addr)
        except socket.timeout:
            raise DeviceIsOffline
        
    def send_unicast(self, **kwargs:Any) -> Dict[str,Any]:
        return self.send(kwargs, self.unicast_addr)

    def send(self, msg:Dict[str,Any], addr:Tuple[str,int]) -> Dict[str,Any]:
        self.sock.sendto(json.dumps(msg).encode(), addr)
        return self.get_answer()

    def get_answer(self) -> Dict[str,Any]:
        data_bytes, addr = self.sock.recvfrom(1024)
        if data_bytes:
            msg = json.loads(data_bytes.decode('utf-8'))
            if isinstance(msg.get('data'), str):
                msg['data'] = json.loads(msg.get('data'))
            return msg
        else:
            return {}
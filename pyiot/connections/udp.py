import socket
from typing import Tuple, Any, Dict
import json
from pyiot.exceptions import DeviceIsOffline

class UdpConnection:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.settimeout(10)

    def send(self, msg:Dict[str,Any], addr:Tuple[str,int], retry:int=3) -> Dict[str,Any]:
        ret = {}
        try:
            self.sock.sendto(json.dumps(msg).encode(), addr)
            ret = self.get_answer()
        except socket.timeout:
            if retry:
                ret = self.send(msg, addr, (retry-1))
            else:
                raise DeviceIsOffline
        return ret

    def get_answer(self) -> Dict[str,Any]:
        data_bytes, addr = self.sock.recvfrom(1024)
        if data_bytes:
            msg = json.loads(data_bytes.decode('utf-8'))
            if isinstance(msg.get('data'), str):
                msg['data'] = json.loads(msg.get('data'))
            return msg
        else:
            return {}

class UdpBroadcastConnection(UdpConnection):
    def __init__(self) -> None:
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        

class UdpListener:
    def __init__(self, ip:str, port:int) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton(ip) + socket.inet_aton('0.0.0.0'))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((ip, port))
    
    def recv(self, bufsize:int = 1024) -> Tuple[bytes, Any]:
        return self.sock.recvfrom(bufsize)
        
import socket
from typing import Tuple, Any, Dict
import json
from pyiot.exceptions import DeviceTimeout

class UdpConnection:
    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.settimeout(10)
        
    def send_json(self, msg:Dict[str,Any], addr:Tuple[str,int], retry:int=3) -> None:
        self.send(json.dumps(msg).encode(), addr, retry=3)

    def send(self, msg:bytes, addr:Tuple[str,int], retry:int=3) -> None:
        try:
            self.sock.sendto(msg, addr)
        except socket.timeout:
            if retry:
                self.send(msg, addr, (retry-1))
            else:
                raise DeviceTimeout
    
    def recv(self, bufsize:int = 1024, retry:int=3) -> Tuple[bytes, Any]:
        ret = tuple() 
        try:
            ret = self.sock.recvfrom(bufsize)
        except socket.timeout:
            if retry:
                ret = self.recv(bufsize, (retry-1))
            else:
                raise DeviceTimeout
        return ret

    def recv_json(self) -> Dict[str,Any]:
        data_bytes, addr = self.sock.recvfrom(1024)
        if data_bytes:
            msg = json.loads(data_bytes.decode('utf-8'))
            if isinstance(msg.get('data'), str):
                msg['data'] = json.loads(msg.get('data'))
            return msg
        else:
            return {}
    
    def __del__(self):
        self.sock.close()

class UdpBroadcastConnection(UdpConnection):
    def __init__(self) -> None:
        super().__init__()
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
        
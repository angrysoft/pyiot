import socket
from typing import Optional, List

class TcpListener:
    pass

class TcpConnection:
    def __init__(self, ip:str, port:int) -> None:
        self.ip = ip
        self.port = port
        self.sock : Optional[socket.socket] = None        
    
    def send_lines(self, lines: List[str], timeout: int = 5):
        try:
            self.sock = socket.create_connection((self.ip, self.port), timeout=timeout)
            for line in lines:
                self.sock.sendall(line.encode())
        except socket.timeout:
            raise DeviceOffline
        
    
    def _make_socket(self):
        pass
import socket
from typing import Optional
from pyiot.exceptions import DeviceTimeout


class TcpListener:
    pass


class TcpConnection:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.sock: Optional[socket.socket] = None

    def send(self, msg: bytes, retry: int = 3, timeout: int = 5) -> None:
        try:
            if self.sock is None:
                self.sock = socket.create_connection(
                    (self.ip, self.port), timeout=timeout
                )
                self.sock.settimeout(5)
            self.sock.sendall(msg)
        except socket.timeout:
            print(f"send retry {retry}")
            if retry:
                self.send(msg, retry=(retry - 1), timeout=timeout)
            else:
                raise DeviceTimeout

    def recv(self, bufsize: int = 1024, retry: int = 3) -> bytes:
        ret: bytes = bytes()
        try:
            ret = self.sock.recv(bufsize)
        except socket.timeout:
            print(f"recv retry {retry}")
            if retry:
                ret = self.recv(bufsize, (retry - 1))
            else:
                raise DeviceTimeout
        return ret

    def close(self):
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.sock = None

from . import WatcherBaseDriver
import socket
import json
from typing import Callable, Optional, Dict, Any


class GatewayWatcher(WatcherBaseDriver):
    def __init__(self):
        self.muliticast = "224.0.0.50"
        self.senderip = "0.0.0.0"
        self.port = 9898
        self._loop = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton(self.muliticast) + socket.inet_aton(self.senderip),
        )
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.muliticast, self.port))

    def watch(self, handler: Callable[[Optional[Dict[str, Any]]], None]) -> None:
        while self._loop:
            data, addr = self.sock.recvfrom(1024)
            msg: Dict[str, Any] = json.loads(data)
            if isinstance(msg.get("data", {}), str):
                msg["data"] = json.loads(msg["data"])
                msg["from"] = addr
            handler(msg)

    def stop(self):
        self._loop = False
        self.sock.close()

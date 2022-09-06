# Copyright 2019 AngrySoft Sebastian Zwierzchowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .udp import UdpBroadcastConnection, UdpConnection
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from hashlib import md5
import struct
import json
from datetime import datetime
from typing import List, Any, Dict, Optional


class MiioPacket:
    def __init__(self, token: str, packet: bytes = b""):
        self.token = bytes.fromhex(token)
        self.key = self.md5sum(self.token)
        self.iv = self.md5sum(self.key + self.token)
        self.magic = (0x21, 0x31)
        self.length = None
        self.unknown1 = 0
        self.device_id = 0x02AF3988
        self.stamp = 0
        self.md5 = None

        if packet:
            self.parse(packet)

    @staticmethod
    def parse_head(raw_packet: bytes):
        """Parse the header of a UDP packet
        Args:
            raw_packet (bytes): raw packet data to parse"""
        head = raw_packet[:32]
        magic, packet_len, unknown1, device_id, stamp, md5 = struct.unpack(
            "!2sHIII16s", head
        )
        return {
            "magic": magic.hex(),
            "packet_len": packet_len,
            "unknown1": unknown1,
            "device_id": device_id,
            "stamp": stamp,
            "checksum": md5.hex(),
        }

    def parse(self, raw_packet: bytes) -> bytes:
        """Parse the payload of a UDP packet.
        Args:
            raw_packet (bytes): raw packet data to parse"""
        decrypted = b""
        head = raw_packet[:32]
        (
            self.magic,
            self.length,
            self.unknown1,
            self.device_id,
            self.stamp,
            self.md5,
        ) = struct.unpack("!2sHIII16s", head)

        data = raw_packet[32:]
        if data:
            cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
            decrypted = cipher.decrypt(data)
            decrypted = unpad(decrypted, 32, style="pkcs7")
        return decrypted

    @property
    def header(self):
        return {
            self.magic,
            self.length,
            self.unknown1,
            self.device_id,
            self.stamp,
            self.md5,
        }

    def generate(self, data: bytes) -> bytes:
        """Generate an encrypted packet from plain data.

        Args:
            data (bytes):
        """

        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        encrypted = cipher.encrypt(pad(data, 64, style="pkcs7"))

        head = struct.pack(
            "!BBHIII16s",
            self.magic[0],
            self.magic[1],  # const magic value
            len(encrypted) + 32,
            self.unknown1,  # unknown const
            self.device_id,  # unknown const
            self.stamp,
            self.token,  # overwritten by the MD5 checksum later
        )

        packet = bytearray(head + encrypted)
        checksum = self.md5sum(bytes(packet))
        for i in range(0, 16):
            packet[i + 16] = checksum[i]
        return bytes(packet)

    def md5sum(self, inp: bytes) -> bytes:
        m = md5()
        m.update(inp)
        return m.digest()

    def __str__(self) -> str:
        return (
            f"{self.token},"
            f"{self.key},"
            f"{self.iv},"
            f"{self.length},"
            f"{self.unknown1},"
            f"{self.device_id},"
            f"{self.stamp},"
            f"{self.md5}"
        )


class MiioConnection:
    def __init__(self, token: str, ip: str, port: int = 54321) -> None:
        self.broad_cast_conn = UdpBroadcastConnection()
        self.conn = UdpConnection()
        self._handshaked: Optional[datetime] = None
        self.ip = ip
        self.port = port
        self.packet = MiioPacket(token)
        # Remember id > 0
        self.id: int = 1

    def check_handshake(self) -> None:
        time_now = datetime.now()
        hello: bytes = b"!1\x00 \xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"

        if self._handshaked is None or (time_now - self._handshaked).seconds > 10:
            self.broad_cast_conn.send(hello, (self.ip, self.port))
            data, addr = self.broad_cast_conn.recv()
            self.packet.parse(data)
            self._handshaked = time_now

    def send(self, method: str, params: List[Any] = []) -> Dict[str, Any]:
        _id: int = self.id
        if _id > 1000:
            _id = 1
        self.id += 1
        _msg: str = json.dumps({"id": _id, "method": method, "params": params})
        _msg += "\r\n"
        self.check_handshake()
        self.conn.send(self.packet.generate(_msg.encode()), (self.ip, self.port))
        self.conn.send("\r\n".encode(), (self.ip, self.port))
        return self._get_result(_id)

    def _get_result(self, _id: int) -> Dict[str, Any]:
        ret = {}
        data_bytes, addr = self.conn.recv()
        if data_bytes:
            try:
                data = self.packet.parse(data_bytes)
                if data:
                    ret: Dict[str, Any] = json.loads(data)
                    if ret.get("id") != _id:
                        ret.clear()

            except json.decoder.JSONDecodeError as err:
                print(err)
        return ret

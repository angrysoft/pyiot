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

from pyiot.connections.udp import UdpBroadcastConnection
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from  hashlib import md5
import struct
import socket


class MiioPacket():
    def __init__(self, token:str, packet=None):
        self.token = bytes.fromhex(token)
        self.key = self.md5sum(self.token)
        self.iv = self.md5sum(self.key + self.token)
        self.magic = (0x21, 0x31)
        self.length = None
        self.unknown1 = 0
        self.device_id = 0x02af3988
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
        magic, packet_len, unknown1, device_id, stamp, md5 = \
            struct.unpack('!2sHIII16s', head)
        return {"magic": magic.hex(),
                "packet_len": packet_len,
                "unknown1": unknown1,
                "device_id": device_id,
                "stamp": stamp,
                "checksum": md5.hex()}

    def parse(self, raw_packet: bytes):
        """Parse the payload of a UDP packet.
            Args:
                raw_packet (bytes): raw packet data to parse"""
        head = raw_packet[:32]
        self.magic, self.length, self.unknown1, self.device_id, self.stamp, self.md5 = \
            struct.unpack('!2sHIII16s', head)
        
        data = raw_packet[32:]
        if data:
            cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
            decrypted = cipher.decrypt(data)
            decrypted = unpad(decrypted, 32, style='pkcs7')
            return decrypted
        
    @property
    def header(self):
        return {self.magic, self.length, self.unknown1, self.device_id, self.stamp, self.md5}

    def generate(self, data: bytes) -> bytes:
        """Generate an encrypted packet from plain data.

        Args:
            data (bytes): 
        """
        
        cipher = AES.new(self.key, AES.MODE_CBC, iv=self.iv)
        encrypted = cipher.encrypt(pad(data, 64, style='pkcs7'))
        
        head = struct.pack(
            '!BBHIII16s',
            self.magic[0], self.magic[1],  # const magic value
            len(encrypted) + 32,
            self.unknown1,  # unknown const
            self.device_id,  # unknown const
            self.stamp,
            self.token  # overwritten by the MD5 checksum later
        )

        
        packet = bytearray(head + encrypted)
        checksum = self.md5sum(packet)
        for i in range(0, 16):
            packet[i+16] = checksum[i]
        return packet
    
    def md5sum(self, inp: bytes) -> bytes:
        m = md5()
        m.update(inp)
        return m.digest()

class MiioConnection:
    def __init__(self) -> None:
        self.conn = UdpBroadcastConnection()
    
    def send_handshake(self, retry=3):
        timeout = 5
        helobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        try:
            sock.sendto(helobytes, (self.ip, 54321))
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            if retry:
                print(f'debug retry handshake {retry}')
                data = self.send_handshake((retry-1))
        return data
        
    def _send(self, method, params=[], retry=2):
        time_now = datetime.datetime.now()
        if not self._handshaked or (time_now - self._handshaked).seconds > 10:
            data = self.send_handshake()
            self.packet.parse(data)
            self._handshaked = time_now
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        _id = self.id
        if _id > 1000:
            _id = 1
        self.id += 1
        _msg = json.dumps({'id': _id,
                           'method': method,
                           'params': params})
        _msg+='\r\n'
        try:
            s.sendto(self.packet.generate(_msg.encode()), (self.ip, self.port))
            ret = self._get_result(s, _id)
        except socket.timeout:
            if retry:
                ret = self._send(method, params, (retry-1))
        return ret
        
    def _get_result(self, sock, _id):
        data_bytes, addr = sock.recvfrom(1024)
        if data_bytes:
            try:
                data = self.packet.parse(data_bytes)
                if not data:
                    return ''
                ret = json.loads(data)
                if ret.get('id') == _id:
                    return ret
            except json.decoder.JSONDecodeError as err:
                print(err)
        return ''
                
            
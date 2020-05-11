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

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from  hashlib import md5
import struct
import socket
from threading import Thread


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

   
class Discover:
    
    @staticmethod
    def discover():
        """Scan for devices in the network.
        This method is used to discover supported devices by sending a
        handshake message to the broadcast address on port 54321.
        """
        timeout = 10        
        addr = "<broadcast>"
        helobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 54321))
        devs = {}
        while True:
            try:
                data, addr = s.recvfrom(1024)
                head = MiioPacket.parse_head(data)
                devs[head['device_id']] = dict(ip=addr[0], port=addr[1])
                devs[head['device_id']].update(head)
            except socket.timeout:
                break  # ignore timeouts on discover
            except Exception as ex:
                break
        return devs


class WatcherBaseDriver:
    def __init__(self):
        pass
    
    def watch(self, handeler):
        pass
    
    def stop(self):
        pass    

    
class Watcher:
    def __init__(self, driver=None):
        self._report_handlers = set()
        if isinstance(driver, WatcherBaseDriver):
            Thread(target=driver.watch, args=(self._handler,), daemon=True).start()
            
    def _handler(self, msg: dict) -> None:
        Thread(target=self._handle_events, args=(msg,)).start()
    
    def add_report_handler(self, handler):
        self._report_handlers.add(handler)
    
    def _handle_events(self, event):
        for handler in self._report_handlers:
            handler(event)
                
            
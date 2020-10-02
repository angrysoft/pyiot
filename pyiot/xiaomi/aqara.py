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

from __future__ import annotations

__all__ = [
    'GatewayWatcher',
    'GatewayInterface',
    #'Gateway',
    'CtrlNeutral',
    'CtrlNeutral2',
    'Plug',
    'SensorSwitchAq2', 
    'Switch',
    'SensorHt',
    'WeatherV1',
    'Magnet',
    'SensorMotionAq2'
    ]


import json
import socket
import binascii
from Cryptodome.Cipher import AES
from pyiot.traits import HumidityStatus, LuminosityStatus, MotionStatus, MutliSwitch, OnOff, OpenClose, PressureStatus, TemperatureStatus, Toggle
from pyiot.connections.udp import UdpConnection
from pyiot.watchers import Watcher, WatcherBaseDriver
from pyiot import BaseDevice
from pyiot.status import Attribute
from typing import Callable, Dict, Any, List, Optional


class GatewayWatcher(WatcherBaseDriver):
    def __init__(self):
        self.muliticast = '224.0.0.50'
        self.senderip = '0.0.0.0'
        self.port = 9898
        self._loop = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                            socket.inet_aton(self.muliticast) + socket.inet_aton(self.senderip))
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.bind((self.muliticast, self.port))

    def watch(self, handler:Callable[[Optional[Dict[str,Any]]], None]) -> None:
        while self._loop:
            data, addr = self.sock.recvfrom(1024)
            msg:Dict[str,Any] = json.loads(data)
            if isinstance(msg.get('data', {}), str):
                msg['data'] = json.loads(msg['data']) 
                msg['from'] = addr
            handler(msg)
    
    def stop(self):
        self._loop = False
        self.sock.close()


class GatewayInterface:
    def __init__(self, ip:str = 'auto', port:int = 9898, sid:str = '', gwpasswd:str = ''):
        self.conn = UdpConnection()
        self.aes_key_iv = bytes([0x17, 0x99, 0x6d, 0x09, 0x3d, 0x28, 0xdd, 0xb3, 0xba, 0x69, 0x5a, 0x2e, 0x6f, 0x58, 0x56, 0x2e])
        self.multicast_addr = ('224.0.0.50', 4321)
        if ip == 'auto':
            gateway: Dict[str, str] = self.whois()
            self.unicast_addr = ( gateway.get('ip', ''), int(gateway.get('port',0)))
            self.sid: str = gateway.get('sid','') 
        else:
            self.unicast_addr = (ip, port)
            self.sid = sid
        self.gwpasswd = gwpasswd
        self._token: str = ''
        self._subdevices:Dict[str, AqaraSubDevice] = dict()
        self.watcher: Watcher = Watcher(GatewayWatcher())
        self.watcher.add_report_handler(self._handle_events)
    
    def register_sub_device(self, dev:AqaraSubDevice):
        self._subdevices[dev.status.sid] = dev
    
    def unregister_sub_device(self, sid:str):
        del self._subdevices[sid]
        
    def _handle_events(self, event:Dict[str,Any]):
        _sid :str = event.get('sid', '')
        if _sid == self.sid and 'token' in event:
            self.token = event['token']
            
        dev = self._subdevices.get(_sid)
        if dev:
            dev.status.update(event.get('data', {}))

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value:str):
        self._token = value

    def whois(self) -> Dict[str, Any]:
        """Discover the gateway device send multicast msg (IP: 224.0.0.50 peer_port: 4321 protocal: UDP)"""
        self.conn.send_json({'cmd': 'whois'}, self.multicast_addr)
        return self.conn.recv_json()

    def get_devices_list(self) -> List[Dict[str,Any]]:
        """The command is sent via unicast to the UDP 9898 port of the gateway,
        which is used to obtain the sub-devices in the gateway."""

        self.conn.send_json({'cmd': 'discovery'}, self.unicast_addr)
        ret = self.conn.recv_json()
        return ret.get('data', [])

    def get_id_list(self) -> List[str]:
        self.conn.send_json({'cmd':'get_id_list'}, self.unicast_addr)
        ret = self.conn.recv_json()
        return ret.get('data', [])

    def read_device(self, sid:str) -> Dict[str, Any]:
        """Reading devices
        Send the "read" command via unicast to the gateway's UDP 9898 port.
        Users can take the initiative to read the attribute status of each device,
        and the gateway returns all the attribute information associated with the device."""

        self.conn.send_json({'cmd': 'read', 'sid': sid}, self.unicast_addr)
        return self.conn.recv_json()

    def write_device(self, model:str, sid:str, short_id:Optional[int]=None, data:Dict[str,Any]={}) -> Dict[str, Any]:
        """Send the "write" command via unicast to the gateway's UDP 9898 port.
        When users need to control the device, the user can use the "write" command."""
        _data = data.copy()
        _data['key'] = self.get_key()
        msg:Dict[str,Any] = dict(cmd='write', model=model, sid=sid)
        if short_id is not None:
            msg['short_id'] = short_id
        if data:
            msg['data'] = _data
        self.conn.send_json(msg, self.unicast_addr)
        return self.conn.recv_json()
    
    def accept_join(self, status: bool = True) -> Dict[str, Any]:
        """Allow adding sub-devices
        
        Args:
            status (bool): True to allow adding sub-device False disallow
        
        Note: The operation to add a sub-device needs to be completed within 30s.
        """
        
        permission = {True: 'yes', False: 'no'}.get(status)
        return self.write_device('gateway', self.sid, 0, {"join_permission": f"{permission}"})
    
    def remove_device(self, sid: str) -> Dict[str, Any]:
        """Delete a sub-device"""
        return self.write_device('gateway', self.sid, 0, {'remove_device': sid})
        
    def refresh_token(self) -> None:
        self.conn.send_json({'cmd': 'get_id_list'}, self.unicast_addr)
        ret = self.conn.recv_json()
        self._token = ret.get('token', '')

    def get_key(self):
        """Get current gateway key"""
        if not self.token:
            self.refresh_token()
        cipher = AES.new(self.gwpasswd.encode('utf8'), AES.MODE_CBC, iv=self.aes_key_iv)
        encrypted = cipher.encrypt(self.token.encode('utf8'))
        return binascii.hexlify(encrypted).decode()
    

class AqaraSubDevice(BaseDevice):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid)
        self.gateway = gateway
        self.status.register_attribute(Attribute('voltage', int))
        self.status.register_attribute(Attribute('short_id', int, readonly=True, oneshot=True))
        self.status.register_attribute(Attribute("low_voltage", int, readonly=True, value=2800))
        self.writable = False
        self.gateway.register_sub_device(self)
    
    def _init_device(self):
        data = self.gateway.read_device(self.status.sid)
        self.status.update(data.get('data', {}))

    def write(self, data:Dict[str, Any]):
        if not self.writable:
            raise PermissionError('Device is not writable')
        self.gateway.write_device(self.status.model,
                                  self.status.sid,
                                  self.status.short_id,
                                  data)
    
                        
# class Gateway(AqaraSubDevice):    
#     def __init__(self, sid:str, gateway:GatewayInterface):
#         super().__init__(sid, gateway)
#         self.writable = True
            
#     def set_rgb(self, red=0, green=0, blue=0, dimmer=255):
#         color = (dimmer << 24) + (red << 16) + (green << 8) + blue
#         return self.write_device('gateway', self.sid, 0, {'rgb': color})

#     def off_led(self):
#         return self.write_device('gateway', self.sid, 0, {'rgb': 0})
    
#     def play_sound(self, sound_id, volume=20):
#         """
#         Play one of standard ringtones or user-defined sound.
#         Args:
#             sound_id (int): 0-8, 10, 13, 20-29 - standard ringtones; >= 10001 - user-defined ringtones uploaded to your gateway via MiHome app
#             volume (int): level from 1 to 100
        
#         Check the reference to get more about sound_id value: https://github.com/louisZL/lumi-gateway-local-api/blob/master/%E7%BD%91%E5%85%B3.md
#         """
#         return self.write_device('gateway', self.sid, 0, {'mid': sound_id, 'vol': volume})

#     def stop_sound(self):
#         """Stop playing any sound from speaker"""
#         return self.write_device('gateway', self.sid, 0, {'mid': 10000})
    
#     def device_status(self):
#         return {**super().device_status(), 'illumination': self.illumination, 'rgb': self.rgb}.copy()
    
#     @property
#     def illumination(self):
#         return self._data.get('illumination', '')
    
#     @property
#     def proto_version(self):
#         return self._data.get('proto_version', '')

#     @property
#     def rgb(self):
#         return int(self._data.get('rgb', -1))
    
#     @rgb.setter
#     def rgb(self, value):
#         self.write_device('gateway', self.sid, 0, {'rgb': value})
        
#     @property
#     def model(self):
#         return self._data.get('model')
    
#     @property
#     def short_id(self):
#         return self._data.get('short_id')
    
class CtrlNeutral(AqaraSubDevice, OnOff):

    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.writable = True
        self.status.add_alias('channel_0', 'power')
        self._init_device()
    
    def on(self):
        self.write({'channel_0': 'on'})
        
    def off(self):
        self.write({'channel_0': 'off'})
    
    def is_on(self) -> bool:
        return self.status.get('channel_0') == "on"
    
    def is_off(self) -> bool:
        return self.status.get('channel_0') == "off"
        

class CtrlNeutral2(AqaraSubDevice, MutliSwitch):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.writable = True
        self.status.register_attribute(Attribute('channel_0', str))
        self.status.register_attribute(Attribute('channel_1', str))
        self._init_device()
        
    def on(self, switch_no:int):
        self.write({f'channel_{switch_no}': 'on'})
        
    def off(self,  switch_no:int):
        self.write({f'channel_{switch_no}': 'off'})
        
    def is_on(self, switch_no:int) -> bool:
        return self.status.get(f'channel_{switch_no}') == "on"
    
    def is_off(self, switch_no:int) -> bool:
        return self.status.get(f'channel_{switch_no}') == "off"
    
    def switches(self) -> List[str]:
        return ['channel_0', 'channel_1']
    
    def switch_no(self) -> int:
        return len(self.switches())


class Plug(AqaraSubDevice, OnOff, Toggle):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.status.add_alias('status', 'power')
        self.status.register_attribute(Attribute('inuse', str))
        self.status.register_attribute(Attribute('power_consumed', str))
        self.status.register_attribute(Attribute('load_power', str))
        self.writable = True
        self._init_device()
    
    def on(self) -> None:
        self.write({'status': 'on'})
        
    def off(self) -> None:
        self.write({'status': 'off'})
        
    def is_on(self) -> bool:
        return self.status.get('status') == "on"
    
    def is_off(self) -> bool:
        return self.status.get('status') == "off"
    
    def toggle(self) -> None:
        self.write({'status': 'toggle'})


class SensorSwitchAq2(AqaraSubDevice):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self._init_device()


class Switch(AqaraSubDevice):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self._init_device()


class SensorHt(AqaraSubDevice, TemperatureStatus, HumidityStatus):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self._init_device()


class WeatherV1(AqaraSubDevice, TemperatureStatus, HumidityStatus, PressureStatus):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self._init_device()
  

class Magnet(AqaraSubDevice, OpenClose):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.status.register_attribute(Attribute('status', str))
        self._init_device()
    
    def is_open(self) -> bool:
        return self.status.status == 'open'
    
    def is_close(self) -> bool:
        return self.status.status == 'close'


class SensorMotionAq2(AqaraSubDevice, MotionStatus, LuminosityStatus):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.status.add_alias('lux', 'luminosity')
        self._init_device()

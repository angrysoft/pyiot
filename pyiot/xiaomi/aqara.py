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

__all__ = ['GatewayWatcher', 'GatewayInterface', 'Gateway', 'CtrlNeutral', 'CtrlNeutral2', 'Plug', 'SensorSwitchAq2', 
           'Switch', 'SensorHt', 'WeatherV1', 'Magnet', 'SensorMotionAq2']


import socket
import json
import binascii
from Cryptodome.Cipher import AES
from datetime import datetime
from pyiot.watcher import Watcher, WatcherBaseDriver
from pyiot.base import BaseDeviceInterface
from pyiot.devicesexceptinos import DeviceIsOffline
from typing import Callable, Dict, Any, List, Optional, Tuple
from __future__ import annotations


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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.settimeout(10)
        self.aes_key_iv = bytes([0x17, 0x99, 0x6d, 0x09, 0x3d, 0x28, 0xdd, 0xb3, 0xba, 0x69, 0x5a, 0x2e, 0x6f, 0x58, 0x56, 0x2e])
        self.multicast: Tuple[str,int] = ('224.0.0.50', 4321)
        if ip == 'auto':
            gateway: Dict[str, str] = self.whois()
            self.unicast = (gateway.get('ip'), int(gateway.get('port',0)))
            self.sid: str = gateway.get('sid','') 
        else:
            self.unicast = (ip, port)
            self.sid = sid
        self.gwpasswd = gwpasswd
        self._token: str = ''
        self._subdevices:Dict[str, AqaraSubDevice] = dict()
        self.watcher: Watcher = Watcher(GatewayWatcher())
        self.watcher.add_report_handler(self._handle_events)
    
    def register_sub_device(self, dev:AqaraSubDevice):
        self._subdevices[dev.sid] = dev
    
    def unregister_sub_device(self, sid):
        del self._subdevices[sid]
        
    def _handle_events(self, event:Dict[str,Any]):
        _sid :str = event.get('sid', '')
        if _sid == self.sid and 'token' in event:
            self.token = event['token']
            
        dev = self._subdevices.get(_sid)
        if dev:
            if event.get('cmd') == 'report':
                dev.report(event)
            elif event.get('cmd') == 'heartbeat':
                dev.heartbeat(event)

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value:str):
        self._token = value

    def whois(self):
        """Discover the gateway device send multicast msg (IP: 224.0.0.50 peer_port: 4321 protocal: UDP)"""
        return self._send_multicast(cmd='whois')

    def get_device_list(self) -> List[Dict[str,Any]]:
        """The command is sent via unicast to the UDP 9898 port of the gateway,
        which is used to obtain the sub-devices in the gateway."""

        return self._send_unicast(cmd='discovery')

    def get_id_list(self) -> List[str]:
        ret = self._send_unicast(cmd='get_id_list')
        return ret.get('data', [])

    def read_device(self, sid:str):
        """Reading devices
        Send the "read" command via unicast to the gateway's UDP 9898 port.
        Users can take the initiative to read the attribute status of each device,
        and the gateway returns all the attribute information associated with the device."""

        return self._send_unicast(cmd='read', sid=sid)

    def write_device(self, model:str, sid:str, short_id:Optional[str]=None, data:Dict[str,Any]={}):
        """Send the "write" command via unicast to the gateway's UDP 9898 port.
        When users need to control the device, the user can use the "write" command."""
        _data = data
        _data['key'] = self.get_key()
        msg:Dict[str,Any] = dict(cmd='write', model=model, sid=sid)
        if short_id is not None:
            msg['short_id'] = short_id
        if data:
            msg['data'] = _data
        return self._send_unicast(cmd='write', model=model, sid=sid, key=self.get_key(), data=data)
        
    def read_all_devices(self):
        id_list = self.get_id_list()
        ret = []
        for _id in id_list:
            ret.append(self.read_device(_id))
        return ret
    
    def accept_join(self, status: bool = True):
        """Allow adding sub-devices
        
        Args:
            status (bool): True to allow adding sub-device False dissalow
        
        Note: The operation to add a sub-device needs to be completed within 30s.
        """
        
        permission = {True: 'yes', False: 'no'}.get(status)
        return self.write_device('gateway', self.sid, 0, {"join_permission": f"{permission}"})
    
    def remove_device(self, sid: str):
        """Delete a sub-device"""
        return self.write_device('gateway', self.sid, 0, {'remove_device': sid})
        
    def refresh_token(self) -> None:
        ret = self._send_unicast(cmd='get_id_list')
        self._token = ret.get('token', '')

    def get_key(self):
        """Get current gateway key"""
        if self.token is None:
            self.refresh_token()
        cipher = AES.new(self.gwpasswd.encode('utf8'), AES.MODE_CBC, iv=self.aes_key_iv)
        encrypted = cipher.encrypt(self.token.encode('utf8'))
        return binascii.hexlify(encrypted).decode()

    def _send_multicast(self, **kwargs:Any) -> Dict[str,Any]:
        try:
            return self._send(kwargs, self.multicast)
        except socket.timeout:
            raise DeviceIsOffline
        
    def _send_unicast(self, **kwargs) -> Dict[str,Any]:
        return self._send(kwargs, self.unicast)

    def _send(self, msg:Dict[str,Any], addr:str) -> Dict[str,Any]:
        self.sock.sendto(json.dumps(msg).encode(), addr)
        return self._answer()

    def _answer(self) -> Dict[str,Any]:
        data_bytes, addr = self.sock.recvfrom(1024)
        if data_bytes:
            msg = json.loads(data_bytes.decode('utf-8'))
            dev_data = msg.get('data')
            if type(dev_data) == str:
                dev_data = json.loads(dev_data)
                msg['data'] = dev_data
            return msg
        else:
            return {}
    
    
class AqaraSubDevice(BaseDeviceInterface):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid)
        self.gateway = gateway
        self._data:Dict[str,Any]
        self._data["voltage"] = 3300
        self._data["low_voltage"] = 2800
        self._init_device()
        self.writable =False
    
    def _init_device(self):
        self.report(self.gateway.read_device(self.sid))
        self.gateway.register_sub_device(self)

    def write(self, data):
        if type(data) is not dict:
            raise ValueError('Data argument is not dict')
        if not self.writable:
            raise PermissionError('Device is not writable')
        self.gateway.write_device(self.model,
                                  self.sid,
                                  self.short_id,
                                  data.get('data'))
    
    @property
    def voltage(self):
        return self._data.get('voltage', -1)
        
    @property
    def short_id(self):
        return self._data.get('short_id')

                        
class Gateway(AqaraSubDevice):    
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.writable = True
            
    def set_rgb(self, red=0, green=0, blue=0, dimmer=255):
        color = (dimmer << 24) + (red << 16) + (green << 8) + blue
        return self.write_device('gateway', self.sid, 0, {'rgb': color})

    def off_led(self):
        return self.write_device('gateway', self.sid, 0, {'rgb': 0})
    
    def play_sound(self, sound_id, volume=20):
        """
        Play one of standard ringtones or user-defined sound.
        Args:
            sound_id (int): 0-8, 10, 13, 20-29 - standard ringtones; >= 10001 - user-defined ringtones uploaded to your gateway via MiHome app
            volume (int): level from 1 to 100
        
        Check the reference to get more about sound_id value: https://github.com/louisZL/lumi-gateway-local-api/blob/master/%E7%BD%91%E5%85%B3.md
        """
        return self.write_device('gateway', self.sid, 0, {'mid': sound_id, 'vol': volume})

    def stop_sound(self):
        """Stop playing any sound from speaker"""
        return self.write_device('gateway', self.sid, 0, {'mid': 10000})
    
    def device_status(self):
        return {**super().device_status(), 'illumination': self.illumination, 'rgb': self.rgb}.copy()
    
    @property
    def illumination(self):
        return self._data.get('illumination', '')
    
    @property
    def proto_version(self):
        return self._data.get('proto_version', '')

    @property
    def rgb(self):
        return int(self._data.get('rgb', -1))
    
    @rgb.setter
    def rgb(self, value):
        self.write_device('gateway', self.sid, 0, {'rgb': value})
        
    @property
    def model(self):
        return self._data.get('model')
    
    @property
    def short_id(self):
        return self._data.get('short_id')
    
class CtrlNeutral(AqaraSubDevice):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.writable = True
        self.channel_0 = Button('channel_0', self)
    
    def on(self):
        self.channel_0.on()
        
    def off(self):
        self.channel_0.off()
    
    def device_status(self):
        return {**super().device_status(), "channel_0": self._data.get("channel_0")}.copy()
        

class CtrlNeutral2(CtrlNeutral):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super().__init__(sid, gateway)
        self.channel_1 = Button('channel_1', self)
    
    def on(self):
        self.write({'data': {'channel_0': 'on', 'channel_1': 'on'}})
        
    def off(self):
        self.write({'data': {'channel_0': 'off', 'channel_1': 'off'}})
    
    def device_status(self):
        return {**super().device_status(), "channel_1": self._data.get("channel_1")}.copy()


class Plug(AqaraSubDevice):
    def __init__(self, sid:str, gateway:GatewayInterface):
        super(Plug, self).__init__(sid, gateway)
        self.power = Button('status', self)
        self.writable = True
    
    @property
    def status(self):
        return self._data.get("status")
    
    def device_status(self):
        return {**super().device_status(), "status": self.status}.copy()


class SensorSwitchAq2(AqaraSubDevice):
    pass


class Switch(AqaraSubDevice):
    @property
    def status(self):
        return self._data.get("status")
    
    def device_status(self):
        return {**super().device_status(), "status": self.status}.copy()


class SensorHt(AqaraSubDevice):
    @property
    def temperature(self) -> str:
        return self._data.get('temperature', '')
    
    @property
    def humidity(self) -> str:
        return self._data.get('humidity', '')
    
    def device_status(self):
        return {**super().device_status(), "temperature": self.temperature, "humidity": self.humidity}.copy()


class WeatherV1(SensorHt):
    @property
    def pressure(self) -> str:
        return self._data.get('pressure', '')
    
    def device_status(self):
        return {**super().device_status(), "pressure": self.pressure}.copy()
        


class Magnet(AqaraSubDevice):
    
    def report(self, data):
        if 'status' in data.get('data', {}):
            data['data']['when'] = datetime.now().isoformat()
        super().report(data)
    
    @property
    def when(self):
        return self._data.get('when', '')
    
    @property
    def status(self):
        return self._data.get('status')
    
    def device_status(self):
        return {**super().device_status(), "status": self.status, "when": self.when}.copy()


class SensorMotionAq2(AqaraSubDevice):
    
    def report(self, data):
        if 'status' in data.get('data', {}):
            data['data']['when'] = datetime.now().isoformat()
        super().report(data)
    
    @property
    def lux(self):
        return self._data.get('lux', -1)

class Button:
    def __init__(self, name, device):
        self.name = name
        self.device = device
        
    def on(self):
        self.device.write({'data': {self.name: 'on'}})

    def off(self):
        self.device.write({'data': {self.name: 'off'}})
    
    def toggle(self):
        self.device.write({'data': {self.name: 'toggle'}})
    
    def is_on(self):
        return self.device._data.get(self.name) == 'on'
        
    def is_off(self):
        return self.device._data.get(self.name) == 'off'
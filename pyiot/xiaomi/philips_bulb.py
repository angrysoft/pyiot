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

__all__ = ['PhilipsBulb', 'PhilipsBulbException']

from typing import List
from pyiot.traits import Dimmer, OnOff, ColorTemperature
from pyiot.base import BaseDevice
from pyiot.discover import DiscoveryMiio
import socket
import json
import datetime
from .protocol import MiioConnection, MiioPacket
from enum import IntEnum
from threading import Thread

class Scene(IntEnum):
    OFF = 0
    BRIGHT = 1
    TV = 2
    WARM = 3
    MIDNIGHT = 4


class PhilipsBulbException(Exception):
    pass


class PhilipsBulbWatcher:
    def __init__(self, dev):
        pass
    
    def watch(self, handler):
        pass

class PhilipsBulb(BaseDevice): # OnOff, Dimmer, ColorTemperature):
    def __init__(self, sid:str, token:str, ip:str = '', port:int = 54321) -> None:
        super().__init__(sid)
        self.ip:str = ip
        self.port:int = port
        if not self.ip:
            discover = DiscoveryMiio()
            dev = discover.find_by_sid(sid)
            self.ip = dev.get('ip','')
            self.port = dev.get('port', 0)
        self.conn = MiioConnection(token=token, ip=self.ip, port=self.port)
        
    # def add_report_handler(self, handler):
    #     self._report_handelers.add(handler)
        
    # def _handle_events(self, event):
    #     for handler in self._report_handelers:
    #         handler(event)
    
    def _init_device(self):
        data = self.get_prop(['power', 'bright', 'cct', 'snm', 'dv'])
        print(data)
    
    def get_prop(self, props: List[str]):
        """
        This method is used to retrieve current property of smart LED.
        
        Args:
            *props (str): Variable length argument name of property to retrive
            
                * `power on` - smart LED is turned on / off: smart LED is turned off
                * `bright` - Brightness percentage. Range 1 ~ 100
                * `cct` - Color temperature. Range 1 ~ 100
                * `snm`
        """
        ret = dict()
        for prop in set(props):
            ret_props = self.conn.send('get_prop', [prop])
            print(ret_props)
            try:
                ret[prop] = ret_props['result'][0]
            except KeyError:
                pass
            except IndexError:
                pass
        return ret
    
    def info(self):
        ret = self.conn.send("miIO.info")
        if 'result' in ret:
            return ret['result']

class PhilipsBulb_old:
    """ Class to controling philips bulb.
    
    Args:
        token (str): device token needed to generate packet
        sid (str): device unique id
        ip (:obj:`str`, optional): ipv4 address to device
        port (:obj:`int`, optional): Port number. Defaults is 54321."""
        
    def __init__(self,token, ip=None, sid=None, port=54321):
        self.sid = sid
        self.ip = ip
        self.port = port
        if not ip:
            self.discover()
        self.id = 1
        self.answers = dict()
        self.packet = MiioPacket(token=token)
        self._report_handelers = set()
        self._handshaked = False
        self._data = dict()
        self._init_device()
        self._report_handelers = set()
        self.cmd = {'set_power': self.set_power,
                    'set_cct': self.set_cct,
                    'set_bright': self.set_bright,
                    'set_ct_pc': self.set_cct}

    def write(self, data):
        _data = data.get('data', {}).copy()
        if not _data:
            raise ValueError('Yeelight write :data is empty')
            return
        c, v = _data.popitem()
        self.cmd.get(c, self._unknown)(v)
    
    def _unknown(self, value):
        raise ValueError(f'unknown parameter {value}')
    
    def report(self, data):
        pass
    
    def heartbeat(self, dats):
        pass
    
    def device_status(self):
        return {'power': self.power, 'bright': self.bright, 'cct': self.cct}
        
    def _init_device(self):
        self._data.update(self.get_prop('power', 'bright', 'cct', 'snm', 'dv'))
        self._data.update(self.info())
    
    def add_report_handler(self, handler):
        self._report_handelers.add(handler)
        
    def _handle_events(self, event):
        for handler in self._report_handelers:
            handler(event)
        
    def discover(self):
        """Scan for devices in the network.
        This method is used to discover supported devices by sending a
        handshake message to the broadcast address on port 54321.
        """
        if self.sid is None:
            raise ValueError("can't find ip without sid")
        timeout = 10
        addr = "<broadcast>"
        helobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 54321))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                head = MiioPacket.parse_head(data)
                if str(head['device_id']) == self.sid:
                    self.ip, self.port = addr
                    break
            except socket.timeout:
                break
            except Exception as ex:
                break
        
    def info(self):
        ret = self._send("miIO.info")
        if 'result' in ret:
            return ret['result']
    
    def refresh(self, *prop):
        data = self.get_prop(*prop)
        self._data.update(data)
        Thread(target=self._handle_events,
               args=({'cmd': 'report', 'sid': self.sid, 'model': self.model, 'data': data},)).start()
        
    def get_prop(self, *props):
        """
        This method is used to retrieve current property of smart LED.
        
        Args:
            *props (str): Variable length argument name of property to retrive
            
                * `power on` - smart LED is turned on / off: smart LED is turned off
                * `bright` - Brightness percentage. Range 1 ~ 100
                * `cct` - Color temperature. Range 1 ~ 100
                * `snm`
        """
        ret = dict()
        for prop in set(props):
            ret_props = self._send('get_prop', [prop])
            try:
                ret[prop] = ret_props['result'][0]
            except KeyError:
                pass
            except IndexError:
                pass
        return ret
        
    def on(self):
        """This method is used to switch on the smart LED"""
        return self.set_power('on')

    def off(self):
        """This method is used to switch off the smart LED"""

        return self.set_power('off')

    def set_power(self, state):
        """This method is used to switch on or off the smart LED (software managed on/off).
        
        Args:
            state (str): can only be `on` or `off`.
                `on` means turn on the smart LED, `off` means turn off the smart LED.
        """
        ret = self._send('set_power', [state])
        self.refresh('power')
        return self._send('set_power', [state])

    def toggle(self):
        """This method is used to toggle the smart LED."""
        if self.is_on:
            return self.off()
        else:
            return self.on()
    
    def set_cct(self, cct):
        f"""This method is used to change the color temperature of a smart LED.
        
        Args:
            ct (int): The target color temperature. 
                The type is integer and range is 1 ~ 100.
        """
        if cct == 0:
            cct = 1
        cct = int(cct)
        self._check_range(cct, 1, 100, msg=f'ct value range 1 - 100')
        ret = self._send('set_cct', [cct])
        self.refresh('cct')
        return ret 

    def set_bright(self, brightness):
        """This method is used to change the brightness of a smart LED.
        
        Args:
            brightness (int): The target brightness. The type is integer and ranges from 1 to 100. 
                The brightness is a percentage instead of a absolute value.
                100 means maximum brightness while 1 means the minimum brightness. 
        """
        
        brightness = int(brightness)
        self._check_range(brightness, begin=1)
        ret =  self._send('set_bright', [brightness])
        self.refresh('bright', 'power')
        return ret 
    
    def set_bricct(self, brightness, cct):
        brightness = int(brightness)
        self._check_range(brightness, begin=1)
        self._check_range(cct, 1, 100, msg=f'ct value range 1 - 100')
        ret = self._send("set_bricct", [brightness, cct])
        self.refresh('cct', 'bright', 'power')
        return ret 
    
    def set_scene(self, scene: Scene):
        """Set scene number."""
        if not isinstance(scene, Scene):
            raise ValueError('Scene s')
        ret =  self._send("apply_fixed_scene", [scene.value])
        self.refresh('snm', 'power')
        return ret
    
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
    
    @staticmethod
    def _check_range(value, begin=0, end=100, msg='not in range'):
        if type(value) is not int or type(begin) is not int or type(end) is not int:
            raise TypeError('int expected')
        
        elif value < begin or value > end:
            raise ValueError(msg)

    def is_on(self):
        return self._data.get('power') == 'on'
    
    def is_off(self):
        return self._data.get('power') == 'off'
     
    @property
    def power(self):
        return self._data.get('power')
    
    @property
    def bright(self):
        return self._data.get('bright')
    
    @property
    def cct(self):
        return self._data.get('cct')
    
    @property
    def ct_pc(self):
        return self._data.get('cct')
    
    @property
    def scene(self):
        return self._data.get('snm')
    
    @property
    def dv(self):
        return self._data.get('dv')
    
    @property
    def model(self):
        return self._data.get('model')
    
    @property
    def ap(self):
        return self._data.get('ap')
    
    @property
    def network(self):
        return self._data.get('netif')
    
    @property
    def firmware_version(self):
        return self._data.get('fw_ver')
    
    @property
    def hardware(self):
        return self._data.get('hw_ver')
    
    @property
    def mac(self):
        return self._data.get('mac')
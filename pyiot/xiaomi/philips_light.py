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

__all__ = ['Candle']

from typing import List, Dict, Any
from pyiot.traits import Dimmer, OnOff, ColorTemperature, Scene
from pyiot import BaseDevice
from pyiot.watchers.philips_light import PhilipsLightWatcher
from pyiot.watchers import Watcher
from pyiot.discover.miio import DiscoverMiio
from pyiot.connections.miio import MiioConnection
from threading import Event


class Candle(BaseDevice, OnOff, Dimmer, ColorTemperature, Scene):
    """ Class to controling philips bulb.
    
    Args:
        token (str): device token needed to generate packet
        sid (str): device unique id
        ip (:obj:`str`, optional): ipv4 address to device
        port (:obj:`int`, optional): Port number. Defaults is 54321."""
        
    def __init__(self, sid:str, token:str, ip:str = '', port:int = 54321) -> None:
        super().__init__(sid)
        self.ip:str = ip
        self.port:int = port
        if not self.ip:
            discover = DiscoverMiio()
            dev = discover.find_by_sid(sid)
            self.ip = dev.get('ip','')
            self.port = dev.get('port', 0)
        self.conn = MiioConnection(token=token, ip=self.ip, port=self.port)
        self.status.add_alias('cct', 'ct_pc')
        self.status.add_alias('snm', 'scene')
        self._init_device()
        
        self._event: Event = None
        self.watcher = Watcher(PhilipsLightWatcher(30, self))
    
    def _init_device(self):
        self.status.update(self.get_prop(['power', 'bright', 'cct', 'snm', 'dv']))
    
    def get_prop(self, props: List[str]) -> Dict[str, Any]:
        """
        This method is used to retrieve current property of smart LED.
        
        Args:
            *props (str): Variable length argument name of property to retrive
            
                * `power` - smart LED is turned on / off: smart LED is turned off
                * `bright` - Brightness percentage. Range 1 ~ 100
                * `cct` - Color temperature. Range 1 ~ 100
                * `snm` -
                * `dv` -
        """
        ret: Dict[str, Any] = {}
        for prop in props:
            ret_props = self.conn.send('get_prop', [prop])
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
    
    def refresh_status(self, attrs: List[str]) -> None:
        data = self.get_prop(attrs)
        if data:
            self.status.update(data)
        if isinstance(self._event, Event) and not self._event.is_set():
            self._event.set()
    
    def on(self):
        """This method is used to switch on the smart LED"""
        self.conn.send('set_power', ['on'])
        self.refresh_status(['power'])
    
    def off(self):
        """This method is used to switch off the smart LED"""
        self.conn.send('set_power', ['off'])
        self.refresh_status(['power'])
    
    def is_on(self):
        return self.status.power == 'on'
    
    def is_off(self):
        return self.status.power == 'off'
    
    def set_bright(self, value:int) -> None:
        """This method is used to change the brightness of a smart LED.
        
        Args:
            value (int): The target brightness. The type is integer and ranges from 1 to 100. 
                The brightness is a percentage instead of a absolute value.
                100 means maximum brightness while 1 means the minimum brightness. 
        """
        self.conn.send('set_bright', [value])
        self.refresh_status(['bright', 'power'])
    
    def set_ct_pc(self, pc:int) -> None:
        f"""This method is used to change the color temperature of a smart LED.
        
        Args:
            pc (int): The target color temperature. 
                The type is integer and range is 1 ~ 100.
        """
        if pc == 0:
            pc = 1

        self.conn.send('set_cct', [int(pc)])
        self.refresh_status(['cct'])
        
    def set_bricct(self, brightness:int , cct :int):
        self.conn.send("set_bricct", [brightness, cct])
        self.refresh_status(['cct', 'bright', 'power']) 
    
    def set_scene(self, scene: Any, args:List[Any] = []) -> None:
        """Set scene number."""
        self.conn.send("apply_fixed_scene", [scene.value])
        self.refresh_status(['snm', 'power'])


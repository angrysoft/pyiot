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
__all__ = ['Yeelight', 'YeelightWatcher', 'Color', 'Bslamp1', 'DeskLamp']
from pyiot.connections import IdGen
from pyiot.exceptions import DeviceIsOffline, DeviceTimeout
from pyiot.connections.tcp import TcpConnection
from pyiot.status import Attribute
from pyiot.traits import ColorTemperature, Dimmer, OnOff, Toggle, Rgb, Hsv
from pyiot.discover import DiscoveryYeelight
import socket
import json
from time import sleep
from enum import Enum
from pyiot.watcher import Watcher, WatcherBaseDriver
from pyiot import BaseDevice
from typing import Dict, List, Any



class YeelightError(Exception):
    pass


class YeelightWatcher(WatcherBaseDriver):
    def __init__(self, dev: YeelightDev):
        self.connection = socket.create_connection((dev.status.ip, dev.status.port))
        self.reader = self.connection.makefile()
        self._loop = True
        self.dev = dev
        
    def watch(self, handler):
        while self._loop:
            _data = dict()
            try:
                jdata = json.loads(self.reader.readline())
            except json.JSONDecodeError as err:
                print(err)
                continue
            
            if 'params' in jdata:
                if 'ct' in jdata['params']:
                    jdata['params']['ct_pc'] = self._ct2pc(int(jdata['params']['ct']))
                # handler({'cmd': 'report',
                #          'sid': self.dev.status.sid,
                #          'model': self.dev.status.model,
                #          'data': jdata['params'].copy()})
                handler(jdata['params'].copy())
    
    def _ct2pc(self, value:int ):
        return int(100 - (self.dev.max_ct - value) / (self.dev.max_ct-self.dev.min_ct) * 100)
        
                
    def stop(self):
        self._loop = False
        self.reader.close()
        self.connection.close()       
        
class YeelightDev(BaseDevice, OnOff, Toggle, Dimmer, ColorTemperature):
    """ Class to controling yeelight devices color bulb BedSide lamp etc.
    
    Args:
        ip (str): ipv4 address to device
        port (:obj:`int`, optional): Port number. Defaults is 55443."""
        
    def __init__(self, sid:str):
        super().__init__(sid)
        self.answers: Dict[str, Any] = dict()
        self.answer_id = IdGen()
        self.min_ct = 1700
        self.max_ct = 6500
        self.efx: str = 'smooth'
        self.duration: int = 500
        self.status.register_attribute(Attribute('ip', str))
        self.status.register_attribute(Attribute('port', int))
        self.status.register_attribute(Attribute('color_mode', int))
        self.status.register_attribute(Attribute('ct', int))
        self._init_device()
        self.conn = TcpConnection(self.status.ip, self.status.port)
        
        self.watcher = Watcher(YeelightWatcher(self))
        self.watcher.add_report_handler(self.status.update)
    
    def _init_device(self):
        dev = DiscoveryYeelight()
        dev = dev.find_by_sid(self.status.sid)
        if not dev:
            raise YeelightError(f'Device is offline {self.status.sid}')
        self.status.update(dev)
    
    # @property
    # def ct_pc(self):
    #     ret =  self._data.get('ct_pc')
    #     if ret is None:
    #         ret = int(100 - (self.max_ct - int(self.ct)) / (self.max_ct-self.min_ct) * 100)
    #         self._data['ct_pc'] = ret
    #     return ret
    
    def get_prop(self, props: List[str]) -> Dict[str, Any]:
        """
        This method is used to retrieve current property of smart LED.
        
        Args:
            props (str): Variable length argument name of property to retrive (max 18 in one)
            
                * `power on` - smart LED is turned on / off: smart LED is turned off
                * `bright` - Brightness percentage. Range 1 ~ 100
                * `ct` - Color temperature. Range 1700 ~ 6500(k)
                * `rgb` -  Color. Range 1 ~ 16777215
                * `hue` - Hue. Range 0 ~ 359
                * `sat` - Saturation. Range 0 ~ 100
                * `color_mode` - 1: rgb mode / 2: color temperature mode / 3: hsv mode
                * `flowing` - 0: no flow is running / 1:color flow is running
                * `delayoff` - The remaining time of a sleep timer. Range 1 ~ 60 (minutes)
                * `flow_params` - Current flow parameters (only meaningful when 'flowing' is 1)
                * `music_on` - 1: Music mode is on / 0: Music mode is off
                * `name` - The name of the device set by “set_name” command
                * `bg_power` - Background light power status
                * `bg_flowing` - Background light is flowing
                * `bg_flow_params` - Current flow parameters of background light
                * `bg_ct` - Color temperature of background light
                * `bg_mode` - 1: rgb mode / 2: color temperature mode / 3: hsv mode
                * `bg_bright` - Brightness percentage of background light
                * `bg_rgb` - Color of background light
                * `bg_hue` - Hue of background light
                * `bg_sat` - Saturation of background light
                * `nl_br` - Brightness of night mode light
                * `active_mode` - ...
        """
        ret: Dict[str, Any] = {}
        
        while props:
            _props_set = props[:17]
            del props[:17]
            _id = self._send('get_prop', _props_set)
            if _id in self.answers:
                ret_props:List[Any] = self.answers.get(_id, {}).get('result', [])
                ret.update(dict(zip(_props_set, ret_props)))
        return ret

    def on(self) -> None:
        """This method is used to switch on the smart LED"""

        self.set_power('on')

    def off(self) -> None:
        """This method is used to switch off the smart LED"""

        self.set_power('off')
    
    def is_on(self):
        return self.status.power == 'on'
    
    def is_off(self):
        return self.status.power == 'off'

    def set_power(self, state:str, mode: int = 0) -> Dict[str,Any]:
        """This method is used to switch on or off the smart LED (software managed on/off).
        
        Args:
            state (str): can only be `on` or `off`.
                `on` means turn on the smart LED, `off` means turn off the smart LED.
            
            mode (:obj:`int`, optional):
                * 0: Normal turn on operation (default value)
                * 1: Turn on and switch to CT mode.
                * 2: Turn on and switch to RGB mode.
                * 3: Turn on and switch to HSV mode.
                * 4: Turn on and switch to color flow mode.
                * 5: Turn on and switch to Night light mode. (Ceiling light only)."""

        if mode not in (0, 1, 2, 3, 4):
            raise ValueError('mode')
        self._send('set_power', [state, self.efx, self.duration, mode])

    def toggle(self):
        """This method is used to toggle the smart LED."""
        self._send('toggle')
    
    def set_ct_pc(self, pc: int):
        """This method is used to change the color temperature of a smart LED with percent scale.
        
        Args:
            percent (int): Percentage target color temperature. 
                The type is integer and range is 0 ~ 100 (%).
                
            efx (:obj:`str`, optional): support two values: `sudden` and `smooth`. 
                If effect is `sudden`, then change will be directly , under this case, parameter `duration` is ignored. 
                If effect is `smooth`, then the total time of gradual change is specified in parameter `duration`.
                Default is `smooth`
            
            duration (:obj:`int`, optional): Specifies the total time of the gradual changing.
                The unit is milliseconds. The minimum support duration is 30 milliseconds.
                Default is `500`
        """
        
        value = self.min_ct + ((self.max_ct - self.min_ct) * pc / 100)
        self.set_ct_abx(int(value))

    def set_ct_abx(self, ct:int):
        """This method is used to change the color temperature of a smart LED.
        
        Args:
            ct (int): The target color temperature. 
                The type is integer and range is 1700 ~ 6500 (k).
                
            efx (:obj:`str`, optional): support two values: `sudden` and `smooth`. 
                If effect is `sudden`, then change will be directly , under this case, parameter `duration` is ignored. 
                If effect is `smooth`, then the total time of gradual change is specified in parameter `duration`.
                Default is `smooth`
            
            duration (:obj:`int`, optional): Specifies the total time of the gradual changing.
                The unit is milliseconds. The minimum support duration is 30 milliseconds.
                Default is `500`"""
                
        self._check_range(ct, self.min_ct, self.max_ct, msg=f'ct value range {self.min_ct} - {self.max_ct}')
        self._send('set_ct_abx', [ct, self.efx, self.duration])

    def set_bright(self, value: int):
        """This method is used to change the brightness of a smart LED.
        
        Args:
            brightness (int): The target brightness. The type is integer and ranges from 1 to 100. 
                The brightness is a percentage instead of a absolute value.
                100 means maximum brightness while 1 means the minimum brightness. 
            
            efx (:obj:`str`, optional): support two values: `sudden` and `smooth`. 
                If effect is `sudden`, then change will be directly , under this case, parameter `duration` is ignored. 
                If effect is `smooth`, then the total time of gradual change is specified in parameter `duration`.
                Default is `smooth`
            
            duration (:obj:`int`, optional): Specifies the total time of the gradual changing.
                The unit is milliseconds. The minimum support duration is 30 milliseconds.
                Default is `500`"""
        self._check_range(value, begin=1)
        self._send('set_bright', [value, self.efx, self.duration])

    def set_default(self):
        """This method is used to save current state of smart LED in persistent memory.
        So if user powers off and then powers on the smart LED again (hard power reset),
        the smart LED will show last saved state."""

        return self._send('set_default')

    def start_cf(self, count=0, action=0, 
                 flow_expression="1000, 2, 2700, 100, 500, 1, 255, 10, 5000, 7, 0,0, 500, 2, 5000, 1"):
        """This method is used to start a color flow. Color flow is a series of smart
        LED visible state changing. It can be brightness changing, color changing or color
        temperature changing. This is the most powerful command. All our recommended scenes,
        e.g. Sunrise/Sunset effect is implemented using this method. With the flow expression, user
        can actually “program” the light effect.
        
        Args:
            count (int): The total number of visible state changing before color flow stopped.
                0 means infinite loop on the state changing.
            action (int): The action taken after the flow is stopped.
                * 0 means smart LED recover to the state before the color flow started.
                * 1 means smart LED stay at the state when the flow is stopped.
                * 2 means turn off the smart LED after the flow is stopped.
            flow_expression (str): is the expression of the state changing series.
        
        Each visible state changing is defined to be a flow tuple that contains 4 elements: [duration, mode, value, brightness].
        A flow expression is a series of flow tuples."""

        self._check_range(action, 0, 2)
        self._send('start_cf', [count, action, flow_expression])

    def stop_cf(self):
        """This method is used to stop a running color flow."""

        self._send('stop_cf')

    def set_scene(self, scene_class: Any, args: List[Any] = []):
        """This method is used to set the smart LED directly to specified state.
        If the smart LED is off, then it will turn on the smart LED firstly and then apply the specified command.
        
        Args:
            scene_class (str):
                * ``color`` means change the smart LED to specified color and brightness.
                * ``hsv`` means change the smart LED to specified color and brightness.
                * ``ct`` means change the smart LED to specified ct and brightness.
                * ``cf`` means start a color flow in specified fashion.
                * ``auto_delay_off`` means turn on the smart LED to specified brightness and 
                    start a sleep timer to turn off the light after the specified minutes.
            
            *args (int): args depends of scene_class """

        params = list()
        params.append(scene_class)
        params.extend(args)
        self._send('set_scene', params)

    def cron_add(self, cron_type, value):
        """This method is used to start a timer job on the smart LED.
        for now only one cron type is working (power off)
        
        Args:
            cron_type (int): Currently can only be 0. (means power off)
            value (int): The length of the timer (in minutes)."""

        if cron_type != 0:
            cron_type = 0

        self._send('cron_add', [cron_type, value])

    def cron_get(self, cron_type):
        """This method is used to retrieve the setting of the current cron job of the specified type.
        
        Args:
            cron_type (int):  the type of the cron job. (currently only support 0)."""

        return self._send('cron_get', cron_type)

    def cron_del(self, cron_type):
        """This method is used to stop the specified cron job.
        
        Args:
            cron_type (int):  the type of the cron job. (currently only support 0)."""

        if cron_type != 0:
            cron_type = 0

        self._send('cron_del' [cron_type])

    def set_adjust(self, action:str, prop:str = 'bright'):
        """This method is used to change brightness, CT or color of a smart LED
        without knowing the current value, it's main used by controllers.
        
        Args:
            action (str): The direction of the adjustment. The valid value can be:
                
                * increase: increase the specified property
                * decrease: decrease the specified property
                * circle: increase the specified property, after it reaches the max value, go back to minimum value.
            prop (str): The property to adjust. The valid value can be:
                
                * bright: adjust brightness.
                * ct: adjust color temperature.
                * color: adjust color. (When “prop" is “color", the “action" can only be “circle", 
                    otherwise, it will be deemed as invalid request.)"""

        if action not in ['increase', 'decrease', 'circle']:
            raise ValueError('action: increase, decrease, circle')
        if prop not in ['bright', 'ct', 'color']:
            raise ValueError('prop: bright, ct, color')
        if prop == 'color':
            action = 'circle'
        self._send('set_adjust', [action, prop])

    def adjust_bright(self, percentage:int):
        """This method is used to adjust the brightness by specified percentage
        within specified duration."""

        self.adjust('adjust_bright', percentage)

    def adjust_ct(self, percentage:int):
        """This method is used to adjust the color temperature by specified
        percentage within specified duration."""

        self.adjust('adjust_ct', percentage)

    def adjust(self, mode:str, percentage:int):

        self._send(mode, [percentage, self.duration])

    def set_name(self, name:str):
        """This method is used to name the device. The name will be stored on the
        device and reported in discovering response. User can also read the name through “get_prop”
        method.
        
        Args:
            name (str): the name of the device"""

        self._send('set_name', [name])
    
    @staticmethod
    def _check_range(value:int, begin:int = 0, end:int = 100, msg: str='not in range'):        
        if value < begin or value > end:
            raise ValueError(msg)
    
    def _send(self, method:str, params: List[Any]=[]) -> int:
        _id:int  = self.answer_id.get_next_id()
        try:
            _msg = json.dumps({'id': _id,
                               'method': method,
                               'params': params})
            self.conn.send(_msg.encode())
            sleep(0.1)
            self.conn.send('\r\n'.encode())
            self._get_result()
        except DeviceIsOffline:
            pass
        except DeviceTimeout:
            pass
        finally:
            self.conn.close()
        return _id
    
    def _get_result(self):
        data_bytes = self.conn.recv(1024, retry=1)
        ret = ''
        if data_bytes:
            try:
                ret = json.loads(data_bytes.decode())
                if 'id' in ret:
                    self.answers[ret.get('id')] = ret
            except json.decoder.JSONDecodeError:
                pass
        

class DeskLamp(YeelightDev):
    def __init__(self, sid:str):
        super().__init__(sid)
        self.min_ct = 2700
        self.max_ct = 6500


class Color(YeelightDev, Rgb, Hsv):
    def __init__(self, sid:str):
        super().__init__(sid=sid)
        
    def set_rgb(self, red: int = 0, green: int = 0, blue: int = 0):
        """This method is used to change the color of a smart LED.
        
        Args:
            red (int): Red color value from 0 to 255.
            green (int): Green color value from 0 to 255.
            blue (int): Blue color value from 0 to 255."""
        rgb = (int(red) << 16) + (int(green) << 8) + int(blue)
        self._send('set_rgb', [rgb, self.efx, self.duration])
    
    def set_color(self, rgb:int):
        """This method is used to change the color of a smart LED.
        
        Args:
            rgb (int): Color value in RGB."""

        self._send('set_rgb', [rgb, self.efx, self.duration])

    def set_hsv(self, hue: int, sat: int):
        """This method is used to change the color of a smart LED.
        
        Args:
            hue (int): The target hue value, whose type is integer.
                It should be expressed in decimal integer ranges from 0 to 359.
            sat (int): The target saturation value whose type is integer. It's range is 0 to 100."""
        
        self._check_range(hue, end=359, msg='hue 0-359')
        self._check_range(sat, msg='sat 0-100')
        return self._send('set_hsv', [hue, sat, self.efx, self.duration])
    
    def adjust_color(self, percentage, duration):
        """This method is used to adjust the color within specified duration."""

        self.adjust('adjust_color', percentage, duration)
    
    def set_music(self, action, host, port):
        """This method is used to start or stop music mode on a device. Under music
        mode, no property will be reported and no message quota is checked.
        
        Args:
            action (int):
            0: turn off music mode.
            1: turn on music mode.,
            host (str): the IP address of the music server.
            port (str): the TCP port music application is listening on.
        
        When control device wants to start music mode, it needs start a TCP
        server firstly and then call “set_music” command to let the device know the IP and Port of the
        TCP listen socket. After received the command, LED device will try to connect the specified
        peer address. If the TCP connection can be established successfully, then control device could
        send all supported commands through this channel without limit to simulate any music effect.
        The control device can stop music mode by explicitly send a stop command or just by closing
        the socket."""

        self._send('set_music', [action, host, port])
    
class Bslamp1(Color):
    pass

    

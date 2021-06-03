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
    'Gateway',
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

from pyiot.zigbee.aqaragateway import AqaraGateway
from pyiot.zigbee import ZigbeeDevice, ZigbeeGateway
from pyiot.traits import Dimmer, HumidityStatus,IlluminanceStatus, MotionStatus, MultiSwitch, \
    OnOff, OpenClose, PressureStatus, Rgb, TemperatureStatus, Toggle
from pyiot.status import Attribute


                     
class Gateway(ZigbeeDevice, Rgb, Dimmer, IlluminanceStatus):    
    def __init__(self, sid:str, gateway: AqaraGateway):
        super().__init__(sid, gateway)
        self.status.register_attribute(Attribute('proto_version', str))
        self.status.bright = 255
        self.gateway.register_sub_device(self)
    
    def set_bright(self, value: int):
        pass
            
    def set_rgb(self, red: int = 0, green: int = 0, blue: int = 0) -> None:
        color = (self.status.bright << 24) + (red << 16) + (green << 8) + blue
        self.set_color(color)
        
    def set_color(self, rgb: int):
        self.gateway.set_device(self.status.sid, {'rgb': rgb})
        

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
      

class CtrlNeutral(ZigbeeDevice, OnOff):

    def __init__(self, sid:str, gateway:ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'ctrl_neutral1'
        self.status.add_alias('channel_0', 'power')
        self.status.add_alias('state', 'power')
        self.gateway.register_sub_device(self)
    
    def on(self):
        self.gateway.send_command(self.status.sid, 'state', 'on')
        
    def off(self):
         self.gateway.send_command(self.status.sid, 'state', 'off')
    
    def is_on(self) -> bool:
        return self.status.get('power').lower() == "on"
    
    def is_off(self) -> bool:
        return self.status.get('power').lower() == "off"
        

class CtrlNeutral2(ZigbeeDevice, MultiSwitch):
    def __init__(self, sid:str, gateway:ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'ctrl_neutral2'
        self.status.register_attribute(Attribute('left', str))
        self.status.register_attribute(Attribute('right', str))
        self.status.add_alias('channel_0', 'left')
        self.status.add_alias('channel_1', 'right')
        self.status.switches = ['left', 'right']
        self.gateway.register_sub_device(self)
        
    def on(self, switch_name:str):
        self.gateway.send_command(self.status.sid, f'{switch_name}', 'on')
        
    def off(self, switch_name:str):
        self.gateway.send_command(self.status.sid, f'{switch_name}', 'off')
        
    def toogle(self, switch_name:str):
        self.gateway.send_command(self.status.sid, f'{switch_name}', 'toogle')
        
    def is_on(self,  switch_name:str) -> bool:
        return self.status.get(switch_name).lower() == "on"
    
    def is_off(self,  switch_name:str) -> bool:
        return self.status.get(switch_name).lower() == "off"


class Plug(ZigbeeDevice, OnOff, Toggle):
    """Model	QBKG03LM"""
    
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'plug'
        self.status.add_alias('status', 'power')
        self.status.register_attribute(Attribute('inuse', str))
        self.status.register_attribute(Attribute('power_consumed', str))
        self.status.register_attribute(Attribute('load_power', str))
        self.gateway.register_sub_device(self)
    
    def on(self) -> None:
        self.gateway.send_command(self.status.sid, 'power', 'on')
        
    def off(self) -> None:
        self.gateway.send_command(self.status.sid, 'power', 'off')
        
    def is_on(self) -> bool:
        return self.status.power.lower() == "on"
    
    def is_off(self) -> bool:
        return self.status.power.lower() == "off"
    
    def toggle(self) -> None:
        self.gateway.send_command(self.status.sid, 'power', 'toggle')


class SensorSwitchAq2(ZigbeeDevice):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'sensor_switch.aq2'
        self.gateway.register_sub_device(self)


class Switch(ZigbeeDevice):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'switch'
        self.gateway.register_sub_device(self)


class SensorHt(ZigbeeDevice, TemperatureStatus, HumidityStatus):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'sensor_ht'
        self.gateway.register_sub_device(self)


class WeatherV1(ZigbeeDevice, TemperatureStatus, HumidityStatus, PressureStatus):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'weather.v1'
        self.gateway.register_sub_device(self)
  

class Magnet(ZigbeeDevice, OpenClose):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'magnet'
        self.gateway.register_sub_device(self)
    
    def is_open(self) -> bool:
        return self.status.status == 'open'
    
    def is_close(self) -> bool:
        return self.status.status == 'close'


class SensorMotionAq2(ZigbeeDevice, MotionStatus, IlluminanceStatus):
    def __init__(self, sid:str, gateway: ZigbeeGateway):
        super().__init__(sid, gateway)
        self.status.model = 'sensor_motion.aq2'
        self.status.add_alias('lux', 'illuminance')
        self.gateway.register_sub_device(self)


class LightDetectionSensor(ZigbeeDevice, IlluminanceStatus):
    """Model	GZCGQ01LM"""
    
    def __init__(self, sid:str, gateway: ZigbeeGateway) -> None:
        super().__init__(sid, gateway)
        self.status.model = 'GZCGQ01LM'
        self.status.register_attribute(Attribute('lux', int))
        self.gateway.register_sub_device(self)

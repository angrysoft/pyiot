__all__ = ['PowerState', 'Pulse', 'Mini', 'DiyPlug']

from .protocol import Discover, EwelinkWatcher
from pyiot.connections.http import HttpConnection
from pyiot.traits import OnOff
from pyiot.watcher import Watcher
from pyiot import BaseDevice, Attribute
from enum import Enum
import json
from typing import Dict, Any

class PowerState(Enum):
    """on: the device is on when power supply is recovered.
    off: the device is off when power supply is recovered.
    stay: the device status keeps as the same as the state before power supply is gone
    """
    ON = 'on'
    OFF = 'off'
    STAY = 'stay'

class Pulse(Enum):
   """on: activate the inching function
   off: disable the inching function
   """
   ON = 'on'
   OFF = 'off'

class BaseSONOFFDIYDevice(BaseDevice, OnOff):
    """Base class for sonnoff DIY device: to parint device you need hotspot with
    WiFi SSID: sonoffDiy
​    WiFi password: 20170618sn
    then you need to discover device and if you have an ip of device you can set new wifi ssid and password with set_wifi method
    """
    def __init__(self, sid:str , ip:str = '', port:int = 8081):
        super().__init__(sid)
        self.status.register_attribute(Attribute('ip', str))
        self.status.register_attribute(Attribute('port', int))
        self.status.register_attribute(Attribute('startup', str))
        self.status.register_attribute(Attribute('pulse', str))
        self.status.register_attribute(Attribute('pulseWidth', str))
        self.status.register_attribute(Attribute('port', int))
        self.status.add_alias('switch', 'power')
        self.status.add_alias('ssid', 'sid')
        
        if ip is None:
            self._find_device()
        else:
            self.status.update({'ip': ip, 'port': port})
        
        self.conn = HttpConnection(url=f'http://{self.status.ip}', port=self.status.port)
        self._init_device()
        self.watcher = Watcher(EwelinkWatcher())
        self.watcher.add_report_handler(self.report)
    
    def report(self, data: Dict[str, Any]):
        if self.status.sid == data.get('id'):
            self.status.update(data)
       
    def _init_device(self):
        self.report(self.info())
        
    def _find_device(self):
        dsc = Discover()
        dev = dsc.search(self.sid)
        if dev:
            self.report(dev)
        
    # def set_power(self, state):
    #     """This method is used to switch on or off.
        
    #     Args:
    #         state (str): can only be `on` or `off`.
    #     """
    #     st = {'on': self.on, 'off': self.off}.get(state)
    #     if st is None:
    #         raise ValueError('state (str): can only be `on` or `off`.')
    #     else:
    #         st()
    
    def on(self):
        """Set power state on"""
        self.conn.post(path='zeroconf/switch', data=self._cmd(switch='on'))
    
    def off(self):
        """Set power state on"""
        self.conn.post(path='zeroconf/switch', data=self._cmd(switch='off'))
    
    def is_on(self):
        return self.status.power == 'on'
    
    def is_off(self):
        return self.status.power == 'off'
        
    def set_power_on_state(self, state:PowerState):
        """Set what device should do when power supply is recovered
        
            Args:
                state (PowerState) 
        """
        if not isinstance(state, PowerState):
            raise ValueError(f"{state} is not instance PowerState")
        self.conn.post(path='zeroconf/startup', data=self._cmd(startup=state.value))
    
    def set_pulse(self, pulse:str, pulse_width:int = 500):
        """Set pulse
        
            Args:
                pulse (Pulse) Pulse.on: activate the inching function;
                              Pulse.off: disable the inching function
                pulse_width (int) Required when "pulse" is on, pulse time length, 
                                  positive integer, ms, only supports multiples of 500 
                                  in range of 500~36000000
        """
        if not isinstance(pulse, Pulse):
            raise ValueError(f"{pulse} is not instance PowerState")
        self.conn.post(path='zeroconf/pulse', data=self._cmd(pulse=pulse.value, pulseWidth=pulse_width))
    
    def set_wifi(self, ssid:str, password:str):
        self.conn.post(path='zeroconf/wifi', data=self._cmd(ssid=ssid, password=password))
    
    def get_info(self):
        resp = self.conn.post(path='zeroconf/info', data=self._cmd())
        if resp.code == 200:
            ret = resp.json.get('data')
            if type(ret) == str:
                ret = json.loads(ret)
            return ret
    
    def get_signal_strength(self) -> int:
        """The WiFi signal strength currently received by the device, negative integer, dBm"""
        resp = self.conn.post(path='zeroconf/signal_strength', data=self._cmd())
        if resp.code == 200:
            return resp.json
        else:
            return 0
    
    def _cmd(self, **kwargs):
        return {'deviceid': self.status.sid, 'data':kwargs}
    
        
class Mini(BaseSONOFFDIYDevice):
    pass


class DiyPlug(BaseSONOFFDIYDevice):
    pass

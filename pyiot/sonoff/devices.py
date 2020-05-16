__all__ = ['PowerState', 'Pulse', 'Mini', 'DiyPlug']

from .protocol import Discover, EwelinkWatcher
from pyiot.session import Session
from pyiot.watcher import Watcher
from pyiot.base import BaseDeviceInterface
from enum import Enum
import json


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

class BaseSONOFFDIYDevice(BaseDeviceInterface):
    """Base class for sonnoff DIY device: to parint device you need hotspot with
    WiFi SSID: sonoffDiy
​    WiFi password: 20170618sn
    then you need to discover device and if you have an ip of device you can set new wifi ssid and password with set_wifi method
    """
    def __init__(self, sid , ip=None, port=8081):
        super().__init__(sid)
        if ip is None:
            self._find_device()
        else:
            self._data.update({'ip': ip, 'port': port})
            
        self._session = Session(url=f'http://{self.ip}', port=self.port)
        self.cmd = {'status': self.set_power}
        self._init_device()
        self.watcher = Watcher(EwelinkWatcher())
        self.watcher.add_report_handler(self.report)
       
    def _init_device(self):
        self.report(self.info())
        
    def _find_device(self):
        dsc = Discover()
        dev = dsc.search(self.sid)
        if dev:
            self.report(dev)
        
    def set_power(self, state):
        """This method is used to switch on or off.
        
        Args:
            state (str): can only be `on` or `off`.
        """
        st = {'on': self.on, 'off': self.off}.get(state)
        if st is None:
            raise ValueError('state (str): can only be `on` or `off`.')
        else:
            st()
    
    def on(self):
        """Set power state on"""
        resp = self._session.post(path='zeroconf/switch', data=self._cmd(switch='on'))
        if resp.code == 200:
            return resp.json
    
    def off(self):
        """Set power state on"""
        resp = self._session.post(path='zeroconf/switch', data=self._cmd(switch='off'))
        if resp.code == 200:
            return resp.json
        
    def set_power_on_state(self, state:PowerState):
        """Set what device should do when power supply is recovered
        
            Args:
                state (PowerState) 
        """
        if not isinstance(state, PowerState):
            raise ValueError(f"{state} is not instance PowerState")
        resp = self._session.post(path='zeroconf/startup', data=self._cmd(startup=state.value))
        if resp.code == 200:
            return resp.json
    
    def set_pulse(self, pulse:str, pulse_width:500):
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
        resp = self._session.post(path='zeroconf/pulse', data=self._cmd(pulse=pulse.value, pulseWidth=pulse_width))
        if resp.code == 200:
            return resp.json
    
    def set_wifi(self, ssid:str, password:str):
        resp = self._session.post(path='zeroconf/wifi', data=self._cmd(ssid=ssid, password=password))
        if resp.code == 200:
            return resp.json
    
    def info(self):
        resp = self._session.post(path='zeroconf/info', data=self._cmd())
        if resp.code == 200:
            ret = resp.json.get('data')
            if type(ret) == str:
                ret = json.loads(ret)
            return ret
    
    def get_signal_strength(self):
        """The WiFi signal strength currently received by the device, negative integer, dBm"""
        resp = self._session.post(path='zeroconf/signal_strength', data=self._cmd())
        if resp.code == 200:
            return resp.json
        else:
            return 0
    
    def is_on(self):
        return self.power == 'on'
    
    def is_off(self):
        return self.power == 'off'
    
    @property
    def ip(self):
        return self._data.get('ip')
    
    @property
    def port(self):
        return self._data.get('port')
    
    
    @property
    def power(self):
        return self._data.get('switch', 'unknown')
    
    @property
    def startup(self):
        return self._data.get('startup', 'unknown')
    
    @property
    def pulse(self):
        return self._data.get('pulse', 'unknown')
    
    @property
    def pulse_width(self):
        return self._data.get('pulseWidth', 'unknown')
    
    @property
    def ssid(self):
        return self._data.get('ssid', 'unknown')
    
    def _cmd(self, **kwargs):
        return {'deviceid': self.sid, 'data':kwargs}
    
    def device_status(self):
        return super().device_status().update({"power": self.power})
    
        
class Mini(BaseSONOFFDIYDevice):
    pass


class DiyPlug(BaseSONOFFDIYDevice):
    pass

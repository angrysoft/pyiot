from __future__ import annotations
from pyiot.status import Attribute
from pyiot import BaseDevice
from pyiot.watchers import Watcher
from pyiot.watchers.clock import ClockWatcher
from pyiot.software import Time
from datetime import datetime
from urllib import request
import json


class Clock(BaseDevice):
    def __init__(self, sid:str):
        super().__init__(sid)
        self.status.register_attribute(Attribute('sunrise', Time))
        self.status.register_attribute(Attribute('sunset', Time))
        self.status.register_attribute(Attribute('time', Time))
        self.status.place = 'all'
        self.watcher = Watcher(ClockWatcher(self))
        self.get_sun_info()
    
    def get_sun_info(self) -> None:
        utcoffset = datetime.now() - datetime.utcnow()
        with request.urlopen('https://api.sunrise-sunset.org/json?lat=52.2319581&lng=21.0067249&formatted=0') as r:
            try:    
                ret = json.loads(r.read().decode())
                if 'results' in  ret:
                    ret = ret['results']
                    sunrise_utc = datetime.fromisoformat(ret.get('sunrise', '')) + utcoffset
                    sunset_utc = datetime.fromisoformat(ret.get('sunset', '')) + utcoffset
                    self.status.sunrise = Time(sunrise_utc.hour, sunrise_utc.minute)
                    self.status.sunset = Time(sunset_utc.hour, sunset_utc.minute)
            except json.JSONDecodeError:
                pass
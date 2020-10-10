from __future__ import annotations
from pyiot.status import Attribute
from pyiot import BaseDevice
from datetime import datetime
from urllib import request
import json


class Time:
    def __init__(self, hour: int = 0, minute:int = 0, seconds: int = 0) -> None:
        self._hour: int = hour
        self._minute: int = minute
        self._seconds: int = seconds
    
    @property
    def hour(self) -> int:
        return self._hour
    
    @property
    def minute(self) -> int:
        return self._minute
    
    @property
    def seconds(self) -> int:
        return self._seconds

    def __eq__(self, value: Time) -> bool:
        return self._hour == value.hour and self._minute == value.minute and self._seconds == value.seconds
    
    def __lt__(self, value: Time) -> bool:
        _local_sec = self._seconds + self._minute * 60 + self._hour * 3600
        _in_sec = value.seconds + value.minute * 60 + value.hour * 3600
        return _local_sec < _in_sec
    
    def __le__(self, value: Time) -> bool:
        return self.__eq__(value) or self.__lt__(value)
    
    def __gt__(self, value: Time) -> bool:
        _local_sec = self._seconds + self._minute * 60 + self._hour * 3600
        _in_sec = value.seconds + value.minute * 60 + value.hour * 3600
        return _local_sec > _in_sec
    
    def __ge__(self, value: Time) -> bool:
        return self.__eq__(value) or self.__gt__(value)
    
    def __repr__(self) -> str:
        return f'{self._hour:02}:{self._minute:02}:{self._seconds:02}'

    

    

class Clock(BaseDevice):
    def __init__(self, sid:str):
        super().__init__(sid)
        self.status.register_attribute(Attribute('sunrise', Time))
        self.status.register_attribute(Attribute('sunset', Time))
        self.status.register_attribute(Attribute('time', Time))
        self.status.place = 'all'

#     async def timer(self):
#         self.sun_info()
#         await self._to_change_min()
#         while True:
#             date = datetime.now()
#             self._time.update({'hour': date.hour, 'minute': date.minute})
#             # bus.emit(f'report.clock.time.{self.time}', {'time': self.time})
#             if self.time == self.sunrise:
#                 # bus.emit(f'report.clock.time.sunrise', {'time': self.time})
#             elif self.time == self.sunset:
#                 # bus.emit(f'report.clock.time.sunset', {'time': self.time})
#             await asyncio.sleep(60)
            
#     async def _to_change_min(self):
#         while datetime.now().second:
#             await asyncio.sleep(1)
    
    def sun_info(self, *args):
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
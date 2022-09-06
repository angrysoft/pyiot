from time import sleep
from datetime import datetime
from . import WatcherBaseDriver
from pyiot import BaseDevice
from pyiot.software import Time
from typing import Callable, Optional, Dict, Any


class ClockWatcher(WatcherBaseDriver):
    def __init__(self, device: Optional[BaseDevice] = None) -> None:
        self.sleep_time = 60
        self._loop = True
        self.device = device

    def watch(self, handler: Callable[[Optional[Dict[str, Any]]], None]) -> None:
        while datetime.now().second:
            sleep(0.5)

        while self._loop:
            _time: Time = Time()
            _time.set_now()

            self.device.status.time = _time
            if _time == Time(1):
                self.device.get_sun_info()

            handler(
                {
                    "cmd": "report",
                    "sid": self.device.status.sid,
                    "data": {
                        "time": str(self.device.status.time),
                        "sunrise": _time == self.device.status.sunrise,
                        "sunset": _time == self.device.status.sunset,
                    },
                }
            )
            sleep(60)

    def stop(self) -> None:
        self._loop = False

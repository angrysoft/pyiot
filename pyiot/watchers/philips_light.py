from threading import Event
from . import WatcherBaseDriver
from pyiot import BaseDevice
from pyiot.exceptions import DeviceTimeout
from typing import Callable, Optional, Dict, Any


class PhilipsLightWatcher(WatcherBaseDriver):
    def __init__(self, sleep_time: int, device: Optional[BaseDevice] = None) -> None:
        self.sleep_time = sleep_time
        self._loop = True
        self.device = device
        self.event = Event()

    def watch(self, handler: Callable[[Optional[Dict[str, Any]]], None]) -> None:
        self.device._event = self.event
        while self._loop:
            old_status: Dict[str, Any] = self.device.status()
            ret = self.event.wait(self.sleep_time)
            if not ret:
                try:
                    self.device.refresh_status(["power", "bright", "cct", "snm", "dv"])
                except DeviceTimeout:
                    self.event.clear()
                    continue

            new_status = self.device.status()
            if new_status != old_status:
                handler(
                    {
                        "cmd": "report",
                        "sid": self.device.status.sid,
                        "model": self.device.status.model,
                        "data": new_status,
                    }
                )
            self.event.clear()

    def stop(self) -> None:
        self._loop = False

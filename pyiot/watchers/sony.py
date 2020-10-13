from typing import Callable
from . import WatcherBaseDriver
from pyiot import BaseDevice
from typing import Callable, Optional, Dict, Any

class BraviaWatcher(WatcherBaseDriver):
    def __init__(self, sleep_time: int, device: Optional[BaseDevice] = None) -> None:
        self.sleep_time = sleep_time
        self._loop = True
        self.device = device

    def watch(self, handler: Callable[[Optional[Dict[str, Any]]], None]) -> None:
        while self._loop:
            old_status: Dict[str, Any] = self.device.status()
            if not self.device.event.wait(self.sleep_time):
                self.device.refresh_status()
            
            new_status = self.device.status()
            if new_status != old_status:
                handler(new_status)
    
    def stop(self) -> None:
        self._loop = False
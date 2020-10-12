from typing import Callable
from . import WatcherBaseDriver
from pyiot import BaseDevice
from typing import Callable, Optional, Dict, Any

class BraviaWatcher(WatcherBaseDriver):
    def __init__(self, sleep_time: int) -> None:
        self.sleep_time = sleep_time

    def watch(self, handler: Callable[[Optional[Dict[str, Any]]], None], device: Optional[BaseDevice] = None) -> None:
        pass
    
    def stop(self) -> None:
        pass
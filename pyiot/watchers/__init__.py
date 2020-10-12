from pyiot import BaseDevice
from threading import Thread
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Set


class WatcherBaseDriver(ABC):
    @abstractmethod
    def watch(self, handler:Callable[[Optional[Dict[str,Any]]], None], device: Optional[BaseDevice] = None) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass  


class Watcher:
    def __init__(self, driver:WatcherBaseDriver):
        self._report_handlers:Set[Callable[[Dict[str,Any]], None]] = set()
        Thread(target=driver.watch, args=(self._handler,), daemon=True).start()
            
    def _handler(self, msg: Dict[str,Any]) -> None:
        Thread(target=self._handle_events, args=(msg,)).start()
    
    def add_report_handler(self, handler:Callable[[Dict[str,Any]], None]) -> None:
        self._report_handlers.add(handler)
    
    def _handle_events(self, event:Dict[str,Any]) -> None:
        for handler in self._report_handlers:
            handler(event)
from abc import ABC, abstractmethod
from pyiot import BaseDevice
from typing import Any, Dict, List


class ZigbeeGateway(ABC):
    @abstractmethod
    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def get_device(self, device_id: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_device_list(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def set_accept_join(self, status: bool = True) -> None:
        pass
    
    @abstractmethod
    def remove_device(self, device_id: str) -> None:
        pass
    
    

class ZigbeeDevice(BaseDevice):
    def __init__(self, sid:str, gateway:ZigbeeGateway):
        super().__init__(sid)
        self.gateway = gateway
        self.status.register_attribute(Attribute('voltage', int))
        self.status.register_attribute(Attribute('short_id', int, readonly=True, oneshot=True))
        self.status.register_attribute(Attribute("low_voltage", int, readonly=True, value=2800))
        self.writable = False
        self.gateway.register_sub_device(self)
        self.watcher = self.gateway.watcher 
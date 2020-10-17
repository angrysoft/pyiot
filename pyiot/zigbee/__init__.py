from __future__ import annotations
from abc import ABC, abstractmethod
from pyiot import BaseDevice
from pyiot.status import Attribute
from pyiot.watchers import Watcher
from typing import Any, Dict, List


class ZigbeeGateway(ABC):
    @abstractmethod
    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        """Set deivice state
        
        Args:
            device_id (str): Device unique identification string
            payload (dict): Device attributes to set
        """
        pass
    
    @abstractmethod
    def get_device(self, device_id: str) -> Dict[str, Any]:
        """Get device attribute status.
        
        Args:
            device_id (str): Device unique identification string
        
        Returns:
            dict: device attributes
        """
        pass
    
    @abstractmethod
    def get_device_list(self) -> List[Dict[str, Any]]:
        """Retrun sub-devices list assigned with gateway
        
        Returns:
            list: sub-devices list
        """
        pass
    
    @abstractmethod
    def set_accept_join(self, status: bool = True) -> None:
        """Allow/Disallow adding sub-devices
        
        Args:
            status (bool): True to allow adding sub-device False disallow
        """
        pass
    
    @abstractmethod
    def remove_device(self, device_id: str) -> None:
        """Delete a sub-device"""
        pass
    
    @abstractmethod
    def register_sub_device(self, device: ZigbeeDevice) -> None:
        """Register sub-device

        Args:
            device (ZigbeeDevice): Device instance
        """
        pass
    
    @abstractmethod
    def get_watcher(self) -> Watcher:
        pass
    
    

class ZigbeeDevice(BaseDevice):
    def __init__(self, sid:str, gateway:ZigbeeGateway):
        super().__init__(sid)
        self.gateway = gateway
        self.status.register_attribute(Attribute('voltage', int))
        self.status.register_attribute(Attribute('linkquality', int))
        self.status.register_attribute(Attribute('short_id', int, readonly=True, oneshot=True))
        self.status.register_attribute(Attribute("low_voltage", int, readonly=True, value=2800))
        self.writable = False
        self.gateway.register_sub_device(self)
        self.watcher: Watcher = self.gateway.get_watcher()
    
    def _init_device(self):
        data = self.gateway.get_device(self.status.sid)
        if 'data' in data:
            self.status.update(data.get('data', {}))
        else:
            self.status.update(data)
        
    
    
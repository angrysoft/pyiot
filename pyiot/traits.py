from abc import ABC, abstractmethod
from typing import Any, Set, Dict, List


class Trait(ABC):
   pass

  
class MutliSwitch(Trait):
    _commands:Set[str] = {'on', 'off'}
    _properties: Dict[str, Any] = {'switch_numbers': 1}
    
    @abstractmethod
    def on(self, switch_no:int):
        pass
    
    @abstractmethod
    def off(self, switch_no:int):
        pass
    
    @abstractmethod
    def is_on(self, switch_no:int) -> bool:
        pass
    
    @abstractmethod
    def is_off(self, switch_no:int) -> bool:
        pass
    
    @abstractmethod
    def switches(self) -> List[str]:
        pass
    
    @abstractmethod
    def switch_no(self) -> int:
        pass

class OnOff(Trait):
    _commands:Set[str] = {'on', 'off'}
    _properties: Dict[str, Any] = {'power': bool}
    
    @abstractmethod
    def on(self) -> None:
        """ Device power on """
        pass
    
    @abstractmethod
    def off(self) -> None:
        pass
    
    @abstractmethod
    def is_on(self) -> bool:
        pass
    
    @abstractmethod
    def is_off(self) -> bool:
        pass
    
class Dimmer(Trait):
    _commands:Set[str] = {'set_bright'}
    _properties: Dict[str, Any] = {'bright': int}
    
    @abstractmethod
    def set_bright(self):
        pass
    

class Toggle(Trait):
    _commands:Set[str] = {'toogle'}
    _properties: Dict[str, Any] = {}
    
    @abstractmethod
    def toggle(self) -> None:
        pass

class OpenClose(Trait):
    _commands:Set[str] = set()
    _properties: Dict[str, Any] = {}
    
    @abstractmethod    
    def is_open(self) -> bool:
        pass
    
    @abstractmethod    
    def is_close(self) -> bool:
        pass

class MotionStatus(Trait):
    _commands:Set[str] = set()
    _properties: Dict[str, Any] = {}

class TemperatureStatus(Trait):
    _commands:Set[str] = set()
    _properties: Dict[str, Any] = {}
    _attributes = {('temperature', str)}

class HumidityStatus(Trait):
    _commands:Set[str] = set()
    _properties: Dict[str, Any] = {}

class PressureStatus(Trait):
    _commands:Set[str] = set()
    _properties: Dict[str, Any] = {}

class LuminosityStatus(Trait):
    _commands:Set[str] = set()
    _properties: Dict[str, Any] = {}


    
    
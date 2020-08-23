from abc import ABC, abstractmethod
from typing import Any, Set, Dict


class Trait(ABC):
    @abstractmethod
    def query(self):
        pass

class OnOff(Trait):
    _commands:Set[str] = {'on', 'off'}
    _properties: Dict[str, Any] = {'power': bool}
    
    @abstractmethod
    def on(self, **kwargs:Any) -> None:
        """ Device power on """
        pass
    
    @abstractmethod
    def off(self, **kwargs:Any) -> None:
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
    _commands:Set[str] = {'set_bright'}
    _properties: Dict[str, Any] = {}
    
    @abstractmethod
    def toggle(self) -> None:
        pass

 
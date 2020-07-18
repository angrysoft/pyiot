from abc import ABC, abstractmethod
from typing import Any, Set, Dict


class Trait(ABC):
    @abstractmethod
    def query(self):
        pass

class OnOff(Trait):
    _commands:Set[str] = {'on', 'off'}
    _propertyies: Dict[str, str] = {'power':'power'}
    
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
    _property: Dict[str, str] = {'bright':'bright'}
    
    @abstractmethod
    def set_bright(self):
        pass
    

class Toggle(Trait):
    def toggle(self) -> None:
        print("toogle")

 
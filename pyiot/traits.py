from abc import ABC, abstractmethod
from typing import Any, Set


class Trait(ABC):
    @abstractmethod
    def query(self):
        pass

class OnOff(Trait):
    _commands:Set[str] = {'on', 'off'}
    
    @abstractmethod
    def on(self, **kwargs:Any) -> None:
        """ Device power on """
        pass
    
    @abstractmethod
    def off(self, **kwargs:Any) -> None:
        pass

    
class Dimmer(Trait):
    _commands:Set[str] = {'dimm'}
    
    @abstractmethod
    def dimm(self):
        pass

class Toggle(Trait):
    def toggle(self) -> None:
        print("toogle")

 
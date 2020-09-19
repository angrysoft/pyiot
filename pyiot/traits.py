from abc import ABC, abstractmethod
from typing import Any, Set, Dict, List, Tuple
from pyiot.status import Attribute


class Trait(ABC):
    pass

  
class MutliSwitch(Trait):
    _commands:Tuple[str,str] = ('on', 'off')
    _attributes: Tuple[Attribute] = tuple()
    
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
    _commands:Tuple[str, str] = ('on', 'off')
    _attributes: Tuple[Attribute] = (Attribute('power', str),)
    
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
    _commands:Tuple[str] = ('set_bright',)
    _attributes: List[Attribute] = [Attribute('bright', int)]
    
    @abstractmethod
    def set_bright(self, value:int):
        pass
    

class Toggle(Trait):
    _commands:Tuple[str] = ('toggle',)
    _attributes: Dict[str, Any] = {}
    
    @abstractmethod
    def toggle(self) -> None:
        pass

class OpenClose(Trait):
    _commands:Set[str] = set()
    _attributes: Tuple[Attribute] = (Attribute('status', str),)
    
    @abstractmethod    
    def is_open(self) -> bool:
        pass
    
    @abstractmethod    
    def is_close(self) -> bool:
        pass


class MotionStatus(Trait):
    _commands:Tuple[str] = tuple()
    _attributes: Tuple[Attribute] = tuple()


class TemperatureStatus(Trait):
    _commands:Tuple[str] = tuple()
    _attributes:Tuple[Attribute] = (Attribute('temperature', str),)


class HumidityStatus(Trait):
    _commands:Tuple[str] = tuple()
    _attributes:Tuple[Attribute] = (Attribute('humidity', str),)

class PressureStatus(Trait):
    _commands:Tuple[str] = tuple()
    _attributes:Tuple[Attribute] = (Attribute('pressure', str),)


class LuminosityStatus(Trait):
    _commands:Tuple[str] = tuple()
    _attributes: Tuple[Attribute] = (Attribute('luminosity', str),)


class ColorTemperature(Trait):
    _commands:Tuple[str] = ('set_ct_pc',)
    _attributes: Tuple[Attribute] = (Attribute('ct_pc', str),)
    
    @abstractmethod
    def set_ct_pc(self, pc:int):
        pass
    
class Rgb(Trait):
    _commands:Tuple[str, str] = ('set_rgb', 'set_color')
    _attributes: Tuple[Attribute] = (Attribute('rgb', str),)
    
    @abstractmethod
    def set_rgb(self, red:int, green:int, blue:int):
        pass
    
    @abstractmethod
    def set_color(self, rgb:int):
        pass

class Hsv(Trait):
    _commands:Tuple[str, str] = ('set_hsv')
    _attributes: Tuple[Attribute] = (Attribute('hue', int), Attribute('sat', int))
    
    @abstractmethod
    def set_rgb(self, red:int, green:int, blue:int):

class Scene(Trait):
    _commands:Tuple[str] = ('set_scene',)
    _attributes: Tuple[Attribute] = (Attribute('scene', str),)
    
    @abstractmethod
    def set_scene(self, scene:Any, args: List[Any] = []):
        pass
    


    
    
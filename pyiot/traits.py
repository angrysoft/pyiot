from abc import ABC, abstractmethod
from typing import Any, Set, List, Tuple
from pyiot.status import Attribute


class Trait(ABC):
    pass

  
class MultiSwitch(Trait):
    _commands:Tuple[str, ...] = ('on', 'off')
    _attributes: Tuple[Attribute, ...] = (Attribute('switches', list, readonly=True, oneshot=True),)
    
    @abstractmethod
    def on(self, switch_name:str):
        pass
    
    @abstractmethod
    def off(self, switch_name:str):
        pass
    
    @abstractmethod
    def toogle(self, switch_name:str):
        pass
    
    @abstractmethod
    def is_on(self, switch_name:str) -> bool:
        pass
    
    @abstractmethod
    def is_off(self, switch_name:str) -> bool:
        pass
    

class OnOff(Trait):
    _commands:Tuple[str, ...] = ('on', 'off')
    _attributes: Tuple[Attribute,  ...] = (Attribute('power', str),)
    
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

class SuspendResume(Trait):
    _commands:Tuple[str, ...] = ('suspend', 'resume')
    _attributes: Tuple[Attribute,  ...] = (Attribute('power_state', str),)
    
    @abstractmethod
    def suspend(self) -> None:
        pass
    
    @abstractmethod
    def resume(self) -> None:
        pass
    
    
class Dimmer(Trait):
    _commands:Tuple[str, ...] = ('set_bright',)
    _attributes: Tuple[Attribute, ...] = (Attribute('bright', int),)
    
    @abstractmethod
    def set_bright(self, value:int):
        pass
    

class Toggle(Trait):
    _commands:Tuple[str, ...] = ('toggle',)
    _attributes: Tuple[Attribute, ...] = tuple()
    
    @abstractmethod
    def toggle(self) -> None:
        pass


class OpenClose(Trait):
    _commands:Set[str] = set()
    _attributes: Tuple[Attribute, ...] = (Attribute('status', str),)
    
    @abstractmethod    
    def is_open(self) -> bool:
        pass
    
    @abstractmethod    
    def is_close(self) -> bool:
        pass


class MotionStatus(Trait):
    _commands:Tuple[str,  ...] = tuple()
    _attributes: Tuple[Attribute, ...] = (Attribute('occupancy', bool), )


class TemperatureStatus(Trait):
    _commands:Tuple[str, ...] = tuple()
    _attributes:Tuple[Attribute] = (Attribute('temperature', str),)


class HumidityStatus(Trait):
    _commands:Tuple[str, ...] = tuple()
    _attributes:Tuple[Attribute] = (Attribute('humidity', str),)

class PressureStatus(Trait):
    _commands:Tuple[str, ...] = tuple()
    _attributes:Tuple[Attribute] = (Attribute('pressure', str),)


class IlluminanceStatus(Trait):
    _commands:Tuple[str, ...] = tuple()
    _attributes: Tuple[Attribute] = (Attribute('illuminance', str),)


class ColorTemperature(Trait):
    _commands:Tuple[str, ...] = ('set_ct_pc',)
    _attributes: Tuple[Attribute] = (Attribute('ct_pc', int),)
    
    @abstractmethod
    def set_ct_pc(self, pc:int):
        pass
    
class Rgb(Trait):
    _commands:Tuple[str, ...] = ('set_rgb', 'set_color')
    _attributes: Tuple[Attribute] = (Attribute('rgb', int),)
    
    @abstractmethod
    def set_rgb(self, red:int, green:int, blue:int):
        pass
    
    @abstractmethod
    def set_color(self, rgb:int):
        pass

class Hsv(Trait):
    _commands:Tuple[str, ...] = ('set_hsv',)
    _attributes: Tuple[Attribute, Attribute] = (Attribute('hue', int), Attribute('sat', int))
    
    @abstractmethod
    def set_hsv(self, hue:int, sat:int):
        pass

class Scene(Trait):
    _commands:Tuple[str, ...] = ('set_scene',)
    _attributes: Tuple[Attribute] = (Attribute('scene', str),)
    
    @abstractmethod
    def set_scene(self, scene:Any, args: List[Any] = []):
        pass
    
class Volume(Trait):
    _commands:Tuple[str, ...] = ('volume_up', 'volume_down', 'set_volume')
    _attributes: Tuple[Attribute] = (Attribute('volume', str),)
    
    @abstractmethod
    def volume_up(self):
        pass
    
    @abstractmethod
    def volume_down(self):
        pass
    
    @abstractmethod
    def set_volume(self, value:int):
        pass
    
    @abstractmethod
    def set_mute(self, status:bool):
        pass
    
class Channels(Trait):
    _commands:Tuple[str, ...] = ('channel_up', 'channel_down', 'set_channel')
    _attributes: Tuple[Attribute] = (Attribute('channel', str),)
    
    @abstractmethod
    def channel_up(self):
        pass
    
    @abstractmethod
    def channel_down(self):
        pass
    
    @abstractmethod
    def set_channel(self, value:int):
        pass

class Arrows(Trait):
    _commands:Tuple[str, ...] = ('up', 'down', 'left', 'right')
    _attributes: Tuple[Attribute,  ...] = tuple()
    
    @abstractmethod
    def up(self):
        pass

    @abstractmethod
    def down(self):
        pass
    
    @abstractmethod
    def left(self):
        pass
    
    @abstractmethod
    def right(self):
        pass

class KeyPad(Trait):
    _commands:Tuple[str, ...] = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'zero')
    _attributes: Tuple[Attribute,  ...] = tuple()

    @abstractmethod
    def one(self):
        pass
    
    @abstractmethod
    def two(self):
        pass

    @abstractmethod
    def three(self):
        pass

    @abstractmethod
    def four(self):
        pass

    @abstractmethod
    def five(self):
        pass

    @abstractmethod
    def six(self):
        pass

    @abstractmethod
    def seven(self):
        pass

    @abstractmethod
    def eight(self):
        pass

    @abstractmethod
    def nine(self):
        pass

    @abstractmethod
    def zero(self):
        pass

class InputSource(Trait):
    _commands:Tuple[str, ...] = ('change_input', )
    _attributes: Tuple[Attribute, ...] = tuple()

    @abstractmethod
    def change_input(self):
        pass

class MediaButtons(Trait):
    _commands:Tuple[str, ...] = ('play', 'pause', 'stop', 'rewind', 'forward')
    _attributes: Tuple[Attribute, ...] = tuple()

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def prev(self):
        pass

    @abstractmethod
    def next(self):
        pass


class ButtonOK(Trait):
    _commands:Tuple[str, ...] = ('ok', )
    _attributes: Tuple[Attribute, ...] = tuple()
    
    @abstractmethod
    def ok(self):
        pass

class ButtonExit(Trait):
    _commands:Tuple[str, ...] = ('exit', )
    _attributes: Tuple[Attribute, ...] = tuple()
    
    @abstractmethod
    def exit(self):
        pass

class ButtonReturn(Trait):
    _commands:Tuple[str, ...] = ('ret', )
    _attributes: Tuple[Attribute, ...] = tuple()
    
    @abstractmethod
    def ret(self):
        pass
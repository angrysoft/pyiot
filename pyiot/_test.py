#!/usr/bin/python
from abc import ABC, abstractmethod
from typing import Any, Set, Dict

class BaseDeviceStatus:
    def __init__(self):
        self._device_data:Dict[str,Any] = {}

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

 
class BaseDevice():
    
    def __new__(cls):
        cls.traits:Set[str] = set()
        cls._cmds:Set[str] = set()
        for _base_class in cls.__bases__:
            _name: str = _base_class.__name__
            if issubclass(_base_class, Trait):
                cls.traits.add(_name)
                cls._cmds.update(_base_class._commands)
        
        return super(BaseDevice, cls).__new__(cls)
    
    def __init__(self):
        
        print('init Basedev')
    
    @property
    def commands(self) -> Set[str]:
        return self._cmds
          
    def execute(self, cmd: str, **kwargs:Any):
        if cmd in self.commands:
            _cmd = getattr(self, cmd)
            _cmd(**kwargs)
                
    def query(self):
        pass
    
    @classmethod    
    def get_bases(cls):
        return cls.__bases__
    

class Dev(BaseDevice, OnOff, Dimmer):
    def __init__(self):
        super().__init__()
    
    def set_power(self, cmd:str, channel:int=0):
        print(f'setting power {cmd} {channel}')
    
    def on(self, **kwargs:int):
        """ i bla lba"""
        if 'channel' in kwargs:
            self.set_power('on', channel=1)
        else:
            self.set_power('on')
    
    def off(self, **kwargs:Any):
        self.set_power('off')
        
    def dimm(self):
        print('dimmer')
    
    

d = Dev()
d.on(channel=3)
d.off()
print(f'Traits {d.traits}')
print(f'Commands {d.commands}')
# print(d.on.__code__.co_argcount)
# d.toggle()

d.execute('on')
d.execute('on', channel=1)
d.execute('off')
d.execute('off', channel=2)

ds = BaseDeviceStatus()
setattr(ds, 'dupa', 1)
print(ds.dupa)


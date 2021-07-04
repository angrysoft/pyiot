from __future__ import annotations
__version__ = '0.2'
from typing import Any, Set, Dict, Tuple, List
from pyiot.status import DeviceStatus, Attribute
from pyiot.traits import Trait
from copy import deepcopy

class BaseDevice:
    def __new__(cls, sid:str, *args: Any, **kwargs: Any):
        cls._traits:Set[str] = set()
        cls._cmds:Set[str] = set()
        cls._attr_list:List[Attribute] = []
        cls._trait_sublases = Trait.__subclasses__()
        cls._get_trait_list(cls.__bases__)
        return object.__new__(cls)
    
    def __init__(self, sid:str) -> None:
        self.status: DeviceStatus = DeviceStatus()
        for _attr in self._attr_list:
            self.status.register_attribute(deepcopy(_attr))
        self.status.register_attribute(Attribute('sid', str, value=sid, readonly=True))
        self.status.register_attribute(Attribute('name', str))
        self.status.register_attribute(Attribute('place', str))
        self.status.register_attribute(Attribute('model', str))
    
    @classmethod
    def _get_trait_list(cls, classes:Tuple[type, ...]) -> None:
        for _base_class in classes:
            if issubclass(_base_class, Trait):
                cls._check_trait(_base_class)
            
    @classmethod
    def _check_trait(cls, _class: object):
        if _class in cls._trait_sublases:
            cls._traits.add(_class.__name__)
            cls._cmds.update(_class._commands)
            _attr : Attribute
            for _attr in _class._attributes:
                cls._attr_list.append(_attr)
        else:
            cls._get_trait_list(_class.__bases__)   
    
    @property
    def commands(self) -> Tuple[str, ...]:
        return tuple(self._cmds)
    
    @property
    def traits(self) -> Tuple[str, ...]:
        return tuple(self._traits)
          
    def execute(self, command:Tuple[str, ...]):
        cmd, *args = command
        if cmd in self.commands:
            _cmd = getattr(self, cmd)
            if args:
                _cmd(*args)
            else:
                _cmd()
                
    def query(self, name:str) -> Any:
        return self.status.get(name)
    
    @classmethod    
    def get_bases(cls):
        return cls.__bases__

    def device_status(self) -> Dict[str, Any]:
        ret = {'traits': self.traits, 'commands': self.commands}
        ret.update(self.status())
        return ret
    
    def get_device_status(self) -> Dict[str, Any]:
        ret:Dict[str, Any] = {'traits': self.traits, 'commands': self.commands}
        status = self.status()
        for item in status:
            ret[item] = str(status[item])
        return ret
__version__ = '0.1'
from typing import Any, Set, Dict
from pyiot.status import DeviceStatus, Attribute
from pyiot.traits import Trait

class BaseDevice:
    def __new__(cls, sid:str, *args: Any, **kwargs: Any):
        cls._traits:Set[str] = set()
        cls._cmds:Set[str] = set()
        cls.status:DeviceStatus = DeviceStatus()
        for _base_class in cls.__bases__:
            _name: str = _base_class.__name__
            if issubclass(_base_class, Trait):
                cls._traits.add(_name)
                cls._cmds.update(_base_class._commands)
                for _attr in _base_class._attributes:
                    cls.status.register_attribute(_attr)
                    # a = Attribute(*_attr)
                    # print(a)
        
        return super(BaseDevice, cls).__new__(cls)
    
    def __init__(self, sid:str) -> None:
        self.status.register_attribute(Attribute('sid', str, value=sid, readonly=True))
        self.status.register_attribute(Attribute('name', str))
        self.status.register_attribute(Attribute('place', str))
        self.status.register_attribute(Attribute('model', str, readonly=True, oneshot=True))
    
    @property
    def commands(self) -> Set[str]:
        return self._cmds
    
    @property
    def traits(self) -> Set[str]:
        return self._traits
          
    def execute(self, cmd: str, **kwargs:Any):
        if cmd in self.commands:
            _cmd = getattr(self, cmd)
            _cmd(**kwargs)
                
    def query(self, name:str) -> Any:
        return self.status.get(name)
    
    @classmethod    
    def get_bases(cls):
        return cls.__bases__

    def device_status(self) -> Dict[str, Any]:
        ret = {'traits': self.traits, 'commands': self.commands}
        ret.update(self.status())
        return ret
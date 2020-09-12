__version__ = '0.1'
from typing import Any, Set, Dict, Tuple
from pyiot.status import DeviceStatus, Attribute
from pyiot.traits import Trait

class BaseDevice:
    def __new__(cls, sid:str, *args: Any, **kwargs: Any):
        cls._traits:Set[str] = set()
        cls._cmds:Set[str] = set()
        cls.status:DeviceStatus = DeviceStatus()
        cls._trait_sublases = Trait.__subclasses__()
        print('type', type(cls.__bases__))
        cls._get_trait_list(cls.__bases__)
        return super(BaseDevice, cls).__new__(cls)
    
    @classmethod
    def _get_trait_list(cls, classes:Tuple[object]) -> None:
        print('clases', classes)
        for _base_class in classes:
            if _base_class in cls._trait_sublases:
                cls._traits.add(_base_class.__name__)
                cls._cmds.update(_base_class._commands)
                for _attr in _base_class._attributes:
                    cls.status.register_attribute(_attr)
            else:    
                for _base_class_bases in _base_class.__bases__:
                    print('else', _base_class_bases, _base_class_bases.__bases__)
                    cls._get_trait_list(_base_class_bases.__bases__)
    
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
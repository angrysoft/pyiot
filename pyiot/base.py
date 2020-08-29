from typing import Set, Any, Dict, Optional
from pyiot.traits import Trait

class Attribute:
    def __init__(self, name:str, attr_type:Any, readonly:bool = False, oneshot: bool = False,
                 value:Optional[Any] = None) -> None:
        self._name = name
        self._type = attr_type
        # TODO : Raise error wehn readony is true and value is not set
        self._readonly = readonly
        self._oneshot = oneshot
        if value is not None:
            self._value = value
        else:
            self._value = attr_type()
    
    @property
    def readonly(self) -> bool:
        return self._readonly
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def value(self) -> Any:
        return self._value
    
    @value.setter
    def value(self, _value:Any):
        if self.readonly:
            if not self._value and self._oneshot:
                self._value = _value
            else:
                raise AttributeError('Readonly')
        else:
            self._value =_value
        
        
class DeviceStatus(object):
    def __init__(self) -> None:
        self.__dict__['_attributes'] = {}
        self.__dict__['_empty'] = Attribute('_empty', str)
    
    def register_attribute(self, attr: Attribute):
        self._attributes[attr.name] = attr
    
    def unregister_attribute(self, attr_name: str):
        del self._attributes[attr_name]
        
    def update(self, value:Dict[str,Any]) -> None:
        for _name in value:
            try:
                self.set(_name, value[_name])
            except AttributeError:
                pass
    
    def get(self, name:str) -> Any:
        return self._attributes.get(name, self._empty).value
    
    def set(self, name:str, value:Any):
        if name in self._attributes:
            self._attributes[name].value = value  
    
    def __getattr__(self, name: str) -> Any:
        if name in self._attributes:
            return self._attributes.get(name, self._empty).value
        else:
            # raise AttributeError(f'object has no attribute {name}')
            return super().__getattribute__(name)
        
    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._attributes:
            self._attributes[name].value = value
        else:
            setattr(self, name, value)
    
    def __call__(self) -> Dict[str, Any]:
        ret = {}
        for attr in self._attributes:
            ret[attr] = self._attributes[attr].value
        return ret
        
    
    
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
                # for _attr in _base_class._attributes:
                    # cls.status.register_attribute(_attr)
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
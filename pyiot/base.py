from typing import Set, Any, Dict
from pyiot.traits import Trait

class Attribute:
    def __init__(self, name:str, attr_type:Any, readonly:bool = True, updateable: bool = False) -> None:
        self._name = name
        self._type = attr_type
        self._value = attr_type()
        self._readonly = readonly
        self._updateable = updateable
    
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
        pass
        
        

class DeviceStatus(object):
    def __init__(self) -> None:
        self._attributes: Dict[str, Any] = {}
    
    def register_attribute(self, attr: Attribute):
        self._attributes[attr.name] = attr
    
    def unregister_attribute(self, attr_name: str):
        del self._attributes[attr_name]
        
    def update(self, value:Dict[str,Any]) -> None:
        for _name in value:
            if _name in self._setters:
                self._data[_name] = value[_name]
            else:
                raise AttributeError('Property readonly')
    
    def get(self, name:str) -> str:
        return getattr(self, name, "")
    
    def set(self, name:str, value:Any):
        if hasattr(self, name):
            setattr(self, name, value)    
    
    # @property
    # def sid(self) -> str:
    #     return self.get("sid")
    
    # @sid.setter
    # def sid(self, value:str) -> None:
    #     _sid:str = self.get('sid')
    #     if not _sid:
    #         self._data['sid'] = value
    #     else:
    #         raise ValueError('Sid alraady set')
        
    
    # @property
    # def name(self) -> str:
    #     return self.get('name')
    
    # @name.setter
    # def name(self, value:str):
    #     self.set('name', value)
    
    # @property
    # def place(self) -> str:
    #     return self.get('place')
    
    # @place.setter
    # def place(self, value:str):
    #     self.set('place', value)
    
    # @property
    # def model(self):
    #     return self.get('model')
    
    # @model.setter
    # def model(self, value:str) -> None:
    #     _model:str = self.get('model')
    #     if not _model:
    #         self._data['model'] = value
    #     else:
    #         raise ValueError('Model alraady set')
    
    def device_status(self) -> Dict[str, str]:
        return {"sid": self.sid, "name": self.name, "place": self.place}
    
    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)
        if name in self._data:
            print('dupa')
        #     return self._data['name']
        
    def __setattribute__(self, name:str , value:Any):
        if name in self._setters:
            self._data[name] = value
        else:
            raise AttributeError('Property readonly')
    
    
class BaseDevice:
    def __new__(cls, sid:str):
        cls._traits:Set[str] = set()
        cls._cmds:Set[str] = set()
        cls.status:DeviceStatus = DeviceStatus()
        for _base_class in cls.__bases__:
            _name: str = _base_class.__name__
            if issubclass(_base_class, Trait):
                cls.traits.add(_name)
                cls._cmds.update(_base_class._commands)
                for _prop in _base_class._properties:
                    cls.status.register_property(_prop, _base_class._properties[_prop])
        
        return super(BaseDevice, cls).__new__(cls)
    
    def __init__(self, sid:str) -> None:
        self.status.sid = sid
    
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

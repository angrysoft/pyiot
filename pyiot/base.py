from typing import Set, Any, Dict
from pyiot.traits import Trait

class DeviceStatus:
    def __init__(self) -> None:
        self._data:Dict[str, Any]
    
    

class BaseDevice:
    def __new__(cls):
        cls._traits:Set[str] = set()
        cls._cmds:Set[str] = set()
        for _base_class in cls.__bases__:
            _name: str = _base_class.__name__
            if issubclass(_base_class, Trait):
                cls.traits.add(_name)
                cls._cmds.update(_base_class._commands)
        
        return super(BaseDevice, cls).__new__(cls)
    
    def __init__(self, sid:str) -> None:
        self._data:DeviceStatus = DeviceStatus()
    
        print('init Basedev')
    
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
        self._data.get(name, '')
    
    
    @classmethod    
    def get_bases(cls):
        return cls.__bases__

class BaseDeviceInterface:
    def __init__(self, sid):
        self._data = dict()
        self._data["sid"] = sid
        self.cmd = dict()
    
    def heartbeat(self, data):
        self.report(data)
    
    def report(self, data:dict) -> None:
        _data = data.copy()
        self._data.update(_data.pop('data', {}))
        self._data.update(_data)
    
    
    @property
    def sid(self):
        return self._data.get("sid")
    
    @property
    def name(self):
        return self._data.get('name', "")
    
    @name.setter
    def name(self, value):
        self._data['name'] = value
    
    @property
    def place(self):
        return self._data.get('place', "")
    
    @place.setter
    def place(self, value):
        self._data['place'] = value
    
    @property
    def model(self):
        return self._data.get('model', 'unknown')
    
    def device_status(self) -> dict:
        return {"sid": self.sid, "name": self.name, "place": self.place}
    
    def sync(self) -> dict:
        pass
    
    def query(self, *params) ->dict:
        pass
    
    def execute(self, command: dict) -> None:
        pass
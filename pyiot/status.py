from typing import Any, Dict, Optional, Callable, List

class Attribute:
    def __init__(self, name:str, attr_type:Any, readonly:bool = False, oneshot: bool = False,
                 value:Optional[Any] = None, setter: Optional[Callable[[Any], None]] = None) -> None:
        self._name = name
        self._type = attr_type
        self._readonly = readonly
        self._oneshot = oneshot
        if value is not None:
            self._value = value
        else:
            self._value = attr_type()
        
        self._setter = setter
    
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
                raise AttributeError(f'{self._name} is readonly')
        else:
            self._value =_value
        
        
class DeviceStatus(object):
    def __init__(self) -> None:
        self.__dict__['_attributes'] = {}
        self.__dict__['_empty'] = Attribute('_empty', str)
    
    def register_attribute(self, attr: Attribute) -> None:
        if attr.name in self._attributes:
            raise AttributeError(f'Attrubute with name {attr.name} already registred')
        self._attributes[attr.name] = attr
    
    def unregister_attribute(self, attr_name: str) -> None:
        if attr_name in self._attributes:
            attr: Attribute = self._attributes[attr_name]
            for _attr in self._attributes:
                if attr is self._attributes[_attr]:
                    del self._attributes[_attr]
        
    def add_alias(self, alias_name:str, attribute_name:str) -> None:
        if alias_name in self._attributes:
            raise ValueError('Alias or attribute allready exist')
        elif attribute_name in self._attributes:
            self._attributes[alias_name] = self._attributes[attribute_name]
        else:
            raise ValueError(f'No registered attribute named {attribute_name}')
        
    def update(self, value:Dict[str,Any]) -> None:
        for _name in value:
            try:
                self.set(_name, value[_name])
            except AttributeError:
                pass
    
    def get(self, name:str) -> Any:
        return self._attributes.get(name, self._empty).value
    
    def set(self, name:str, value:Any) -> None:
        if name in self._attributes:
            self._attributes[name].value = value
    
    def get_names(self) -> List[str]:
        return list(self._attributes.keys())
    
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
            print(name, value)
            # setattr(self, name, value)
    
    def __call__(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = {}
        for attr in self._attributes:
            ret[attr] = self._attributes[attr].value
        return ret
        
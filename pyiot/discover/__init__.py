from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Discovery:
    engines = []
    
    def __init__(self):
        pass
  
  
class BaseDiscovery(ABC):
    @abstractmethod
    def find_all(self) -> List[Dict[str,Any]]:
        pass
    
    @abstractmethod
    def find_by_sid(self, sid:str) -> Dict[str,Any]:
        pass  


class DiscoveryAqara(BaseDiscovery):
    pass

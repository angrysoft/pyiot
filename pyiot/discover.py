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
    
    def find_by_sid(self, sid:str) -> Dict[str,Any]:
        pass  

class DiscoverySonoff(BaseDiscovery):
    pass

class DiscoverySony(BaseDiscovery):
    pass

class DiscoveryYeelight(BaseDiscovery):
    pass

class DiscoveryAqara(BaseDiscovery):
    pass

class DiscoveryMiio(BaseDiscovery):
    pass

Discover.engines.append(DiscoverySonoff())

if __name__ == "__main__":
    d = Discover()
    print(d.engines)
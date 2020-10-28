from typing import Dict, Any


class Converter:
    def __init__(self) -> None:
        self._devices_to_gateway: Dict[str, Dict[str, str]] = {}
        self._devices_to_status: Dict[str, Dict[str, str]] = {}
    
    def add_device(self, model: str, parameters: Dict[str, Any]):
        self._devices_to_gateway[model] = parameters
        self._devices_to_status[model] = {}
        for param in parameters:
            self._devices_to_status[model][parameters[param]] = param
    
    def to_gateway(self, model: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        ret = {}
        # try:
        for param in parameters:
            param_name = self._devices_to_gateway[model][param]
            ret[param_name] = parameters[param]
            print(param, param_name)
        # except KeyError as e:
        #     print('error', e)
        print('to gate', ret)
        return ret
    
    def to_status(self, model: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        ret = {}
        try:
            for param in parameters:
                param_name = self._devices_to_status[model][param]
                ret[param_name] = parameters[param]
        except KeyError as e:
            print(e)
        print('to stat', ret)
        return ret

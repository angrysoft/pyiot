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
        return self._convert(self._devices_to_gateway, model, parameters)

    def to_status(self, model: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return self._convert(self._devices_to_status, model, parameters)

    def _convert(
        self, source_parameters: Dict[str, Any], model: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        ret = {}
        for param in parameters:
            device_parameters = source_parameters.get(model, {})
            param_name = device_parameters.get(param, param)
            ret[param_name] = parameters[param]
        return ret

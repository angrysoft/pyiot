from . import ZigbeeGateway, ZigbeeDevice
import paho.mqtt.client as mqqt
import json
from typing import Any, Dict, List


class Zigbee2mqttGateway(ZigbeeGateway):
    def __init__(self, host: str = 'localhost', port: int = 1882, user: str ='', password: str ='', ssl: bool = False) -> None:
        self._client = mqqt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect("localhost", 1883, 60)
        self._client.loop_start()

    def _on_connect(self):
        pass
    
    def _on_message(self):
        pass
    
    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        pass
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        pass
    
    def get_device_list(self) -> List[Dict[str, Any]]:
        pass
    
    def set_accept_join(self, status: bool) -> None:
        pass
    
    def register_sub_device(self, device: ZigbeeDevice) -> None:
        pass
    
    def remove_device(self, device_id: str) -> None:
        pass
    
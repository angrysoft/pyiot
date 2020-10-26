from . import ZigbeeGateway, ZigbeeDevice
from pyiot.watchers import Watcher
from pyiot.watchers.zigbee2mqtt import Zigbee2mqttWatcher
import json
import paho.mqtt.client as mqqt
from typing import Any, Dict, List


class Zigbee2mqttGateway(ZigbeeGateway):
    def __init__(self, host: str = 'localhost', port: int = 1882, user: str ='', password: str ='', ssl: bool = False) -> None:
        self._client = mqqt.Client()
        self._client.connect("localhost", 1883, 60)
        self._subdevices:Dict[str, ZigbeeDevice] = dict()
        self.watcher: Watcher = Watcher(Zigbee2mqttWatcher(self._client))
        self.watcher.add_report_handler(self._handle_events)
    
    def _handle_events(self, event:Dict[str,Any]):
        print('foo info: ', event)
        # _sid: str = event.get('sid', '')
        # if _sid == self.sid and 'token' in event:
        #     self.token = event['token']
            
        # dev = self._subdevices.get(_sid)
        # if dev:
        #     dev.status.update(event.get('data', {}))
        
    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        self._client.publish(f"zigbee2mqtt/{device_id}/set", json.dumps(payload))
    
    def send_command(self,device_id: str, argument_name: str, value: str):
        payload = Zigbee2mqttPayload(argument_name, value)
        self.set_device(device_id, payload.get_payload())
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        return {}
    
    def get_device_list(self) -> List[Dict[str, Any]]:
        self._client.publish("zigbee2mqtt/bridge/config/devices/get ", '')
        return []
    
    def set_accept_join(self, status: bool) -> None:
        string_status = {True: 'true', False: 'false'}
        self._client.publish("zigbee2mqtt/bridge/config/permit_join", string_status.get(status))
    
    def register_sub_device(self, device: ZigbeeDevice) -> None:
        # TODO : send get devicei attributes
        self._subdevices[device.status.sid] = device
    
    def unregister_sub_device(self, device_id: str) -> None:
        pass
    
    def remove_device(self, device_id: str) -> None:
        self._client.publish("zigbee2mqtt/bridge/config/remove", device_id)
    
    def get_watcher(self) -> Watcher:
        return self.watcher
    
    
class Zigbee2mqttPayload: #(ZigbeePayload):
    def __init__(self, argument_name:str, value:str) -> None:
        if value in ['on', 'off', 'toggle']:
            self._value = value.upper()
        else:
            self._value = value
            
        self._argument_name = argument_name
        self._arguments = {'status': 'state', 'power': 'state'}
        
    def get_payload(self) -> Dict[str, Any]:
        ret = {}
        ret[self._arguments.get(self._argument_name, self._argument_name)] = self._value.upper()
        return ret
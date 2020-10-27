from . import ZigbeeGateway, ZigbeeDevice
from pyiot.watchers import Watcher
from pyiot.watchers.zigbee2mqtt import Zigbee2mqttWatcher
import json
import paho.mqtt.client as mqqt
from typing import Any, Dict, List


class Zigbee2mqttGateway(ZigbeeGateway):
    def __init__(self, host: str = 'localhost', port: int = 1882, user: str ='', password: str ='', ssl: bool = False) -> None:
        self._topics = set()
        self._client = mqqt.Client()
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnet
        self._client.connect("localhost", 1883, 60)
        self._subdevices:Dict[str, ZigbeeDevice] = dict()
        self.watcher: Watcher = Watcher(Zigbee2mqttWatcher(self._client))
        self.watcher.add_report_handler(self._handle_events)
        
    def _on_connect(self, client, userdata, flags, rc):
        self._connected = True
        for topic in self._topics:
            client.subscribe(topic)
        
    def _on_disconnet(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            client.reconnect()
            
    def add_topic(self, topic:str) -> None:
        self._topics.add(topic)
        self._client.subscribe(topic)
    
    def del_topic(self, topic:str) -> None:
        self._topics.remove(topic)
        self._client.unsubscribe(topic)
    
    def _handle_events(self, event:Dict[str,Any]):
        dev = self._subdevices.get(event.get('sid',''))
        if dev:
            # c = Converter(dev.status.model, event)
            # dev.status.update(c.to_device())
            dev.status.update(event)
        
    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        self._client.publish(f"zigbee2mqtt/{device_id}/set", json.dumps(payload))
    
    def send_command(self,device_id: str, argument_name: str, value: str):
        # dev = self._subdevices.get(device_id)
        # if dev:
            # c = Converter(dev.status.model, dict(argument_name=value)
            # dev.status.update(c.to_device())
            # self.set_device(device_id, c.to_gateway('zigbee2mqtt')
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
        self.add_topic(f"zigbee2mqtt/{device.status.sid}")
        print(device.status.get_attr_names())
        for x in device.status.get_attr_names():
            if not x in ['sid', 'name', 'place', 'short_id']:
                payload = Zigbee2mqttPayload(x, "")
                self._client.publish(f"zigbee2mqtt/{device.status.sid}/get", json.dumps(payload.get_payload()))
    
    def unregister_sub_device(self, device_id: str) -> None:
        self.del_topic(f"zigbee2mqtt/{device_id}")
        del self._subdevices[device_id]
    
    def remove_device(self, device_id: str) -> None:
        self._client.publish("zigbee2mqtt/bridge/config/remove", device_id)
    
    def get_watcher(self) -> Watcher:
        return self.watcher
    
    
class Zigbee2mqttPayload: #(ZigbeePayload):
    def __init__(self, argument_name:str, value:str) -> None:
        # if value in ['on', 'off', 'toggle']:
        #     self._value = value.upper()
        # else:
        self._value = value
            
        self._argument_name = argument_name
        self._arguments = {'status': 'state', 'power': 'state'}
        
    def get_payload(self) -> Dict[str, Any]:
        ret = {}
        ret[self._arguments.get(self._argument_name, self._argument_name)] = self._value.upper()
        return ret
    
    def ret_payload(self):
        ret = {}
        ret[self._arguments.get(self._argument_name, self._argument_name)] = self._value.lower()
        return ret
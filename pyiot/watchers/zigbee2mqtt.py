from . import WatcherBaseDriver
from typing import Callable, Optional, Dict, Any
from os.path import basename
import json
from pyiot.zigbee.converter import Converter


class Zigbee2mqttWatcher(WatcherBaseDriver):
    def __init__(self, client):
        self._client = client
        self._client.on_message = self._on_message
        self._connected = False
        self._handler = None
        self._loop = True
            
    def _on_message(self, client, userdata, message):
        # print(message.topic, json.loads(message.payload))
        msg = {}
        msg['sid'] = basename(message.topic)
        msg.update(json.loads(message.payload))
        self._handler(msg)

    def watch(self, handler:Callable[[Optional[Dict[str,Any]]], None]) -> None:
        while self._loop:
            self._handler = handler
            self._client.loop()
    
    def stop(self):
        self._loop = False
from . import WatcherBaseDriver
from typing import Callable, Optional, Dict, Any
from os.path import dirname


class Zigbee2mqttWatcher(WatcherBaseDriver):
    def __init__(self, client):
        self._client = client
        self._client.on_message = self._on_message
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnet
        self._connected = False
        self._handler = None
        
    def _on_connect(self, client, userdata, flags, rc):
        self._connected = True
        client.subscribe('zigbee2mqtt/#')
    
    def _on_message(self, client, userdata, message):
        msg = {}
        msg['sid'] = dirname(message.topic)
        msg.update(message.payload)
        slef._handler(msg)
        
    def _on_disconnet(self, client, userdata, rc):
        self._connected = False
        if rc != 0:
            client.reconnect()
            
        
    def watch(self, handler:Callable[[Optional[Dict[str,Any]]], None]) -> None:
        while self._loop:
            self._handler = handler
            self._client.loop()
    
    def stop(self):
        self._loop = False
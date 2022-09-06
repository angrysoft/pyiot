from . import WatcherBaseDriver
from typing import Callable, Optional, Dict, Any
from os.path import basename
import json


class Zigbee2mqttWatcher(WatcherBaseDriver):
    def __init__(self, client, gateway):
        self._gateway = gateway
        self._client = client
        self._client.on_message = self._on_message
        self._connected = False
        self._handler = None
        self._loop = True

    def _on_message(self, client, userdata, message):
        msg = {}
        msg["cmd"] = "report"
        msg["sid"] = basename(message.topic)
        dev = self._gateway._subdevices.get(msg["sid"])
        if dev:
            msg["data"] = self._gateway._converter.to_status(
                dev.status.model, json.loads(message.payload)
            )
            dev.status.update(msg["data"])
        else:
            msg["data"] = json.loads(message.payload)
        self._handler(msg)

    def watch(self, handler: Callable[[Optional[Dict[str, Any]]], None]) -> None:
        while self._loop:
            self._handler = handler
            self._client.loop_forever()

    def stop(self):
        self._loop = False

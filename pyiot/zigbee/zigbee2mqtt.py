from pyiot.zigbee.converter import Converter
from . import ZigbeeGateway, ZigbeeDevice
from pyiot.zigbee.converter import Converter
from pyiot.watchers import Watcher
from pyiot.watchers.zigbee2mqtt import Zigbee2mqttWatcher
import json
import paho.mqtt.client as mqtt
from typing import Any, Callable, Dict, List, Set


class Zigbee2mqttGateway(ZigbeeGateway):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        user: str = "",
        password: str = "",
        ssl: bool = False,
        sid: str = "",
    ) -> None:
        self._topics: Set[str] = set()
        self._client: mqtt.Client = mqtt.Client()
        self._client.on_connect: Callable[[...], None] = self._on_connect
        self._client.on_disconnect = self._on_disconnet
        if user and password:
            self._client.username_pw_set(username=user, password=password)
        self._client.connect(host=host, port=port, keepalive=60)
        self._subdevices: Dict[str, ZigbeeDevice] = dict()
        self._converter = Converter()
        self.watcher: Watcher = Watcher(Zigbee2mqttWatcher(self._client, self))

    def _on_connect(
        self, client: mqtt.Client, userdata: Any, flags: Any, rc: Any
    ) -> None:
        self._connected = True
        to_subscribe: Set[str] = self._topics.copy()
        for topic in to_subscribe:
            client.subscribe(topic)

    def _on_disconnet(self, client: mqtt.Client, userdata: Any, rc: Any):
        self._connected = False
        if rc != 0:
            client.reconnect()

    def add_topic(self, topic: str) -> None:
        self._topics.add(topic)
        self._client.subscribe(topic)

    def del_topic(self, topic: str) -> None:
        self._topics.remove(topic)
        self._client.unsubscribe(topic)

    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        self._client.publish(f"zigbee2mqtt/{device_id}/set", json.dumps(payload))

    def send_command(self, device_id: str, argument_name: str, value: str):
        dev = self._subdevices.get(device_id)
        if dev:
            self.set_device(
                device_id,
                self._converter.to_gateway(dev.status.model, {argument_name: value}),
            )

    def get_device(self, device_id: str) -> Dict[str, Any]:
        return {}

    def get_device_list(self) -> List[Dict[str, Any]]:
        self._client.publish("zigbee2mqtt/bridge/config/devices/get", "")
        return []

    def set_accept_join(self, status: bool) -> None:
        string_status = {True: "true", False: "false"}
        self._client.publish(
            "zigbee2mqtt/bridge/config/permit_join", string_status.get(status)
        )

    def register_sub_device(self, device: ZigbeeDevice) -> None:
        self._subdevices[device.status.sid] = device
        self.add_topic(f"zigbee2mqtt/{device.status.sid}")
        self._converter.add_device(
            device.status.model, payloads.get(device.status.model, {})
        )
        # payload: Dict[str, str] = payloads.get(device.status.model, {})
        for x in statuses.get(device.status.model, []):
            self._client.publish(
                f"zigbee2mqtt/{device.status.sid}/get", f'{{"{x}":""}}'
            )

    def unregister_sub_device(self, device_id: str) -> None:
        self.del_topic(f"zigbee2mqtt/{device_id}")
        del self._subdevices[device_id]

    def remove_device(self, device_id: str) -> None:
        self._client.publish("zigbee2mqtt/bridge/config/remove", device_id)

    def get_watcher(self) -> Watcher:
        return self.watcher


# device model : device : gateway
payloads = {
    "ctrl_neutral1": {"power": "state", "linkquality": "linkquality"},
    "ctrl_neutral2": {
        "left": "state_left",
        "right": "state_right",
        "linkquality": "linkquality",
    },
    "plug": {
        "power": "state",
        "power_consumed": "consumption",
        "linkquality": "linkquality",
        "load_power": "power",
        "toggle": "toggle",
    },
    "magnet": {"contact": "contact", "linkquality": "linkquality"},
    "weather.v1": {
        "temperature": "temperature",
        "humidity": "humidity",
        "linkquality": "linkquality",
    },
    "sensor_ht": {
        "temperature": "temperature",
        "humidity": "humidity",
        "pressure": "pressure",
        "linkquality": "linkquality",
    },
    "sensor_motion.aq2": {
        "occupancy": "occupancy",
        "illuminance": "illuminance",
        "linkquality": "linkquality",
    },
    "switch": {
        "click": "single",
        "doubleclick": "double",
        "tripleclick": "triple",
        "linkquality": "linkquality",
    },
    "sensor_switch.aq2": {
        "click": "single",
        "doubleclick": "double",
        "long_press": "long",
        "long_press_release": "long_release",
        "linkquality": "linkquality",
    },
    "GZCGQ01LM": {
        "illuminance": "illuminance",
        "lux": "illuminance_lux",
        "linkquality": "linkquality",
    },
    "SNZB01": {"linkquality": "linkquality"},
    "SNZB02": {"contact": "contact", "linkquality": "linkquality"},
    "SNZB03": {"occupancy": "occupancy", "linkquality": "linkquality"},
}

statuses = {
    "ctrl_neutral1": ["state"],
    "ctrl_neutral2": ["state_left", "state_right"],
    "plug": ["state"],
    "magnet": [],
    "weather.v1": [],
    "sensor_ht": [],
    "sensor_motion.aq2": [],
    "switch": [],
    "sensor_switch.aq2": [],
    "GZCGQ01LM": [],
    "SNZB01": [],
    "SNZB02": [],
    "SNZB03": [],
}

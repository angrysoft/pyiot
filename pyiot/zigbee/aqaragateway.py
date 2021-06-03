from __future__ import annotations
import binascii
from pyiot.zigbee.converter import Converter
from Cryptodome.Cipher import AES
from pyiot.zigbee import ZigbeeGateway, ZigbeeDevice
from pyiot.connections.udp import UdpConnection
from pyiot.watchers.aqara import GatewayWatcher
from pyiot.watchers import Watcher
from typing import Any, Dict, List

class AqaraGateway(ZigbeeGateway):
    def __init__(self, ip:str = 'auto', port:int = 9898, sid:str = '', gwpasswd:str = ''):
        self._converter = Converter()
        self.conn = UdpConnection()
        self.aes_key_iv = bytes([0x17, 0x99, 0x6d, 0x09, 0x3d, 0x28, 0xdd, 0xb3, 0xba, 0x69, 0x5a, 0x2e, 0x6f, 0x58, 0x56, 0x2e])
        self.multicast_addr = ('224.0.0.50', 4321)
        if ip == 'auto':
            gateway: Dict[str, str] = self.whois()
            self.unicast_addr = ( gateway.get('ip', ''), int(gateway.get('port',0)))
            self.sid: str = gateway.get('sid','') 
        else:
            self.unicast_addr = (ip, port)
            self.sid = sid
        self.gwpasswd = gwpasswd
        self._token: str = ''
        self._subdevices:Dict[str, ZigbeeDevice] = dict()
        self.watcher: Watcher = Watcher(GatewayWatcher())
        self.watcher.add_report_handler(self._handle_events)
    
    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value:str):
        self._token = value
    
    def refresh_token(self) -> None:
        self.conn.send_json({'cmd': 'get_id_list'}, self.unicast_addr)
        ret = self.conn.recv_json()
        self._token = ret.get('token', '')

    def get_key(self):
        """Get current gateway key"""
        if not self.token:
            self.refresh_token()
        cipher = AES.new(self.gwpasswd.encode('utf8'), AES.MODE_CBC, iv=self.aes_key_iv)
        encrypted = cipher.encrypt(self.token.encode('utf8'))
        return binascii.hexlify(encrypted).decode()
    
    def whois(self) -> Dict[str, Any]:
        """Discover the gateway device send multicast msg (IP: 224.0.0.50 peer_port: 4321 protocal: UDP)"""
        self.conn.send_json({'cmd': 'whois'}, self.multicast_addr)
        return self.conn.recv_json()
        
    def _handle_events(self, event:Dict[str,Any]):
        _sid: str = event.get('sid', '')
        if _sid == self.sid and 'token' in event:
            self.token = event['token']
            
        dev = self._subdevices.get(event.get('sid',''))
        if dev:
            dev.status.update(self._converter.to_status(dev.status.model, event.get('data', {})))
    
    def set_device(self, device_id: str, payload: Dict[str, Any]) -> None:
        _payload = payload.copy()
        _payload['key'] = self.get_key()
        self.conn.send_json({'cmd': 'write',
                             'sid': device_id,
                             'data': _payload}, self.unicast_addr)
        self.conn.recv_json()
            
    def send_command(self,device_id: str, argument_name: str, value: str):
        dev = self._subdevices.get(device_id)
        if dev:
            self.set_device(device_id, self._converter.to_gateway(dev.status.model, {argument_name: value}))
    
    def get_device(self, device_id: str) -> Dict[str, Any]:
        self.conn.send_json({'cmd': 'read', 'sid': device_id}, self.unicast_addr)
        ret =  self.conn.recv_json()
        if ret.get('sid', '') == device_id:
            return ret
        else:
            return {}
    
    def get_device_list(self) -> List[Dict[str, Any]]:
        self.conn.send_json({'cmd':'get_id_list'}, self.unicast_addr)
        sid_list = self.conn.recv_json()
        ret = []
        for sid in sid_list.get('data', []):
            ret.append(self.get_device(sid))
        return ret
    
    def set_accept_join(self, status: bool) -> None:
        permission = {True: 'yes', False: 'no'}.get(status)
        self.set_device(self.sid, {"join_permission": f"{permission}"})
    
    def remove_device(self, device_id: str) -> None:
        self.set_device(self.sid, {'remove_device': device_id})
    
    def register_sub_device(self, device: ZigbeeDevice):
        self._subdevices[device.status.sid] = device
        self._converter.add_device(device.status.model, payloads.get(device.status.model, {}))
        self.conn.send_json({'cmd': 'read', 'sid': device.status.sid}, self.unicast_addr)
        ret =  self.conn.recv_json()
        if ret.get('sid', '') == device.status.sid:
            device.status.update(self._converter.to_status(ret.get('model', ''), ret.get('data', {})))
    
    def unregister_sub_device(self, device_id:str):
        del self._subdevices[device_id]
        
    def get_watcher(self) -> Watcher:
        return self.watcher
    

# device model : device : gateway
payloads = {
    'ctrl_neutral1': {'state': 'channel_0', 'linkquality': 'linkquality'},
    'ctrl_neutral2': {'left': 'channel_0', 'right': 'channel_1', 'linkquality': 'linkquality'},
    'plug': {'power': 'status', 'power_consumed': 'power_consumed', 'linkquality': 'linkquality', 'load_power': 'load_power', 'toggle': 'toggle'},
    'magnet': {'status': 'status'},
    'weather.v1': {'temperature': 'temperature', 'humidity': 'humidity'},
    'sensor_ht': {'temperature': 'temperature', 'humidity': 'humidity', 'pressure': 'pressure'},
    'sensor_motion.aq2': {'occupancy': 'occupancy', 'illuminance': 'illuminance'},
    'switch': {'state': 'status', 'doubleclick': 'doubleclick', 'tripleclick': 'tripleclick'},
    'sensor_switch.aq2': {'click': 'single', 'doubleclick': 'double', 'long_press': 'long', 'long_press_release': 'long_release click'},
}
from pyiot.status import Attribute
from pyiot.connections.http import HttpConnection, Response
from pyiot import BaseDevice
from pyiot.traits import Channels, OnOff, Volume
import socket
from threading import Thread
import struct
from typing import Dict, Any, List


# Copyright 2019 AngrySoft Sebastian Zwierzchowski
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Bravia(BaseDevice, OnOff, Volume, Channels):
    """Navigate to: [Settings] → [Network] → [Home Network Setup] → [IP Control]
        Set [Authentication] to [Normal and Pre-Shared Key]
        There should be a new menu entry [Pre-Shared Key]. Set it for example to 0000.
    """

    def __init__(self, ip:str, macaddres: str = '', psk:str = '0000', sid:str = '', model:str = 'Unknown'):
        super().__init__(sid)
        self.status.register_attribute(Attribute('ip', str, value=ip))
        self.status.register_attribute(Attribute('psk', str, value=psk))
        self.status.register_attribute(Attribute('ircc_codes', dict))
        self.status.register_attribute(Attribute('mac', str, value=macaddres))
        self.status.add_alias('cid', 'sid')
        self._report_handelers = set()
        self.conn = HttpConnection(f'http://{ip}/sony')
        self.conn.add_header('X-Auth-PSK', self.status.psk)
        self._dev_init()
    
    def _dev_init(self):
        if self.is_on():
            self.ircc_code = self.get_all_commands()
            self.status.update(self.get_system_info())
    
    def add_report_handler(self, handler):
        self._report_handelers.add(handler)
        
    def _handle_events(self, event):
        for handler in self._report_handelers:
            handler(event)
    
    def refresh_status(self):
        data = self.get_content_info()
        if data:
            self.status.update(data)
            Thread(target=self._handle_events,
                   args=({'cmd': 'report', 'sid': self.status.sid, 'model': self.status.model, 'data': data},)).start()
        
    
    def _check_power_status(self) -> None:
        """This API provides the current power status of the device."""
        power: str = 'off'
        try:
            self.conn.timeout = 2
            ret: Response = self.conn.post(path='system', data=self._cmd("getPowerStatus"))
            if ret.code == 200:
                result = ret.json
                if 'result' in result:
                    status = result['result'][0].get('status')
                    if status == 'standby':
                        power = 'standby'
                    elif status == 'active':
                        power = 'on'
        except socket.error:
            pass
        except Exception:
            pass
        
        self.status.power = power
        
    def on(self):
        """Power on tv"""
        # TODO: check if this wakeup tv when is in standby mode
        mac: str = self.status.mac.replace(":", "")
        data: bytes = b'FFFFFFFFFFFF' + (mac * 20).encode()
        send_data: bytes = b''

        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
            send_data += struct.pack('B', int(data[i: i + 2], 16))
        
        # Broadcast it to the LAN.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(send_data, ('255.255.255.255', 7))
     
    def off(self):
        """Power off tv"""
        self.conn.post(path='system', data=self._cmd('setPowerStatus', params=[{"status": False}]))
        
    def is_on(self):
        self._check_power_status()
        return self.status.power == 'on'
    
    def is_off(self) -> bool:
        self._check_power_status()
        return self.status.power in ('off', 'standby')
    
    def volume_up(self):
        self.send_ircc('VolumeUp')
    
    def volume_down(self):
        self.send_ircc('VolumeDown')
    
    def channel_up(self):
        self.send_ircc('ChannelUp')
    
    def channel_down(self):
        self.send_ircc('ChannelDown')
    
    def set_channel(self, value: int):
        pass
    
    def get_supported_api(self):
        """This API provides the supported services and their information"""
        
        return self._send('guide', 'getSupportedApiInfo', [{"services": []}])
    
    def get_interface_information(self):
        """This API provides information of the REST API interface provided by the server. This API must not include private information."""
        return self._send('system', 'getInterfaceInformation')
    
    def get_system_info(self):
        """This API provides general information on the device."""
        return self._send('system', 'getSystemInformation')
    
    def get_supported_function(self):
        """his API provides the list of device capabilities within the scope of system service handling."""
        return self._send('system', 'getSystemSupportedFunction')
    
    def get_connected_sources(self):
        """This API provides information on the current status of all external input sources of the device."""
        
        return self._send('avContent', 'getCurrentExternalInputsStatus')
    
    def get_application_list(self):
        """This API provides the list of applications that can be launched by setActiveApp"""
        
        return self._send('appControl', 'getApplicationList')

    
    def get_application_status(self):
        """This API provides the status of the application itself or the accompanying status related to a specific application."""
        
        return self._send('appControl', 'getApplicationStatusList')
    
    def get_content_info(self):
        """This API provides information of the currently playing content or the currently selected input."""
        return self._send('avContent', 'getPlayingContentInfo')
    
    def get_sources(self):
        """This API provides the list of sources in the scheme."""
        return self._send('avContent', 'getSourceList', [{"scheme": "extInput"}])
    
    def set_sources(self, exinput: str, extype: str = 'tuner', port:str = '1', trip:str = '', srv: str = ''):
        """This API provides the list of sources in the scheme."""
        ext = {'hdmi': f'extInput:hdmi?port={port}',
               'component': f'extInput:component?port={port}',
               'widi': f'extInput:widi?port={port}',
               'cec': f'extInput:cec?type={extype}&port={port}',
               'tv': f'tv:dvbt?trip={trip}&srvName={srv}'}.get(exinput)
        if ext is None:
            raise ValueError(f'Incorrect input {exinput}')
        self.conn.post(path='avContent', data=self._cmd('setPlayContent', params=[{"uri": f"{ext}"}]))
        
    def set_sources_uri(self, uri:str):
        self.conn.post(path='avContent', data=self._cmd('setPlayContent', params=[{"uri": f"{uri}"}]))
    
    def get_sound_settings(self, target: str = ''):
        """This API provides the current settings and supported settings related to the sound configuration items."""
        
        return self._send('audio', 'getSoundSettings', [{'target': f'{target}'}])
    
    def get_speaker_settings(self):
        """TThis API provides current settings and supported settings related to speaker configuration items."""
        
        return self._send('audio', 'getSpeakerSettings', [{'target': ''}])
    
    def set_mute(self, status:bool):
        """This API provides the function to change the audio mute status.
        
        Args:
            status (bool)"""
        self.conn.post(path='audio', data=self._cmd('setAudioMute', params=[{"status": status}]))
    
    def get_volume(self):
        return self._send('audio', 'getVolumeInformation')
    
    def set_volume(self, value:int, target: str = ''):
        self.conn.post(path='audio', data=self._cmd('setAudioVolume', params=[{"volume": f'{value}',"target": target}], pid=666))

    def get_all_commands(self) -> Dict[str,Any]:
        ret = self.conn.post(path='system', data=self._cmd('getRemoteControllerInfo'))
        try:
            result = ret.json['result'][1]
            commands: Dict[str,Any] = dict()
            for func in result:
                if 'name' in func:
                    commands[func.get('name')] = func.get('value')
        except:
            return {}
        return commands
    
    def send_ircc(self, name:str):
        """Send command codes of IR remote. (InfraRed Compatible Control over Internet Protocol)
        
        Args:
            name (str): name of command to send
        """
        try:
            if not self.status.ircc_codes:
                self.ircc_code = self.get_all_commands()
            code = self.ircc_code.get(name)
        except AttributeError:
            raise BraviaError(message=f'Ircc name not recognize {name}')
        
        headers = {'SOAPACTION': '"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC"',
                   'Content-Type': 'text/xml; charset=UTF-8',
                   'Accept': '*/*'}
        
        data = f'<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">' \
            f'<s:Body>' \
            f'<u:X_SendIRCC xmlns:u="urn:schemas-sony-com:service:IRCC:1">' \
            f'<IRCCCode>{code}</IRCCCode>' \
            f'</u:X_SendIRCC>' \
            f'</s:Body>' \
            f'</s:Envelope>'
        self.conn.post(path='IRCC', headers=headers, raw=data)
        self.refresh_status()

    @staticmethod
    def _cmd(cmd: str, params: List[Any] = [], pid: int = 10, version: str = '1.0') -> Dict[str, Any]:
        return {'method': cmd, 'params': params, 'id': pid, 'version': version}

    def _send(self, path:str, cmd: str, params: List[Any] = []) -> Dict[str, Any]:
        ret: Dict[str, Any] = {}
        resp = self.conn.post(path=path, data=self._cmd(cmd, params))
        if resp.code == 200:
            ret =  self._parse_result(resp.json)
        return ret
    
    def _parse_result(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        ret: Dict[str, Any] = {}
        if type(msg) is dict:
            if 'error' in msg:
                raise BraviaError(msg['error'])
            elif 'result' in msg and msg['result']:
                ret = msg['result'][0]
        return ret

class BraviaError(Exception):
    _codes = {
        2: 'Timeout',
        3: 'Illegal Argument',
        5: 'Illegal Request',
        12: 'No Such Method',
        14: 'Unsupported Version'
        }
    
    def __init__(self, code: List[int]=[], message: str =f'Unknow Error') -> None:
        self._code_no = 0
        if code:
            self.message = self._codes.get(code[0], code)
            self._code_no = code[0]
        else:
            self.message = message
    
    def __str__(self):
        return self.message
    
    @property
    def code_no(self):
        return self._code_no
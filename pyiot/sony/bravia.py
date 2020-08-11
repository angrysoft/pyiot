from pyiot.session import Session
import json
import socket
from threading import Thread
import struct


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


###########################################################
#
#	DISCOVER IP VIA SSDP PROTOCOL (UDP 1900 PORT)
#
###########################################################
# def DISCOVER_via_SSDP (service = "urn:schemas-sony-com:service:ScalarWebAPI:1"):
# 	import select, re
# 	SSDP_ADDR = "239.255.255.250";
# 	SSDP_PORT = 1900;
# 	SSDP_MX = 1;
# 	SSDP_ST = service;

# 	ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
# 		"HOST: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
# 		"MAN: \"ssdp:discover\"\r\n" + \
# 		"MX: %d\r\n" % (SSDP_MX, ) + \
# 		"ST: %s\r\n" % (SSDP_ST, ) + "\r\n";

# 	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 	#select.select([sock], [], [], 10)
# 	sock.settimeout(5.0)
# 	dest = socket.gethostbyname(SSDP_ADDR)
# 	sock.sendto(ssdpRequest, (dest, SSDP_PORT))
# 	sock.settimeout(5.0)
# 	try: 
# 		data = sock.recv(1000)
# 	except socket.timeout:
# 		print "No Bravia found (timed out)!"
# 		sys.exit(1)
# 	response = data.decode('utf-8')
# 	match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", response)
# 	if match:                      
# 		return match.group()
# 	else:
# 		return SONYIP
from enum import Enum
class BraviaConst(Enum):
    MULTICAST = '239.255.255.250'
    PORT = 1900
    MX = 1
    ST = 'urn:schemas-sony-com:service:ScalarWebAPI:1'
    SEARCH_REQUEST = 'M-SEARCH * HTTP/1.1\r\n' \
                     'HOST: 239.255.255.250:1900\r\n' \
                     'MAN: "ssdp:discover"\r\n' \
                     'MX: 1\r\n' \
                     'ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n'.encode()

class Discover:
    """Class to dicover yeelight devices connectetd to local network
    
    Examples:
        >>> y = Yeelight()
        >>> y.discover()
    """

    def search(self, timeout=10, sid=None):
        """Discover devices
        
        Args:
            timeout (int): socket timeout"""
        devices = dict()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        sock.settimeout(timeout)
        sock.sendto(BraviaConst.SEARCH_REQUEST.value, (BraviaConst.MULTICAST.value, BraviaConst.PORT.value))
        while True:
            try:
                data, addr = sock.recvfrom(1024)
            except OSError:
                break
            if data:
                dev = self._parse_devices(data.decode(), addr)
                if dev:
                    if sid is None:
                        devices[dev['id']] = dev
                    elif sid == dev['id']:
                        devices = dev
                        break
                    
        sock.close()
        return devices

    def _parse_devices(self, data_in, addr):
        dev = {}
        print(data_in)
        for d in data_in.split('\r\n'):
            if d == 'HTTP/1.1 200 OK':
                if dev:
                    self.devices[dev['id']] = dev
                    dev = {}
            d = d.lower()
            if d.startswith('cache-control') or d.startswith('date') or d.startswith('ext'):
                continue
            if d.find(':') > 0:
                key, val = d.split(':', 1)
                val = val.strip()
                if key == 'support':
                    val = val.split(' ')
                elif key == 'location':
                    url = urlparse(val)
                    dev['ip'] = url.hostname
                    dev['port'] = url.port
                dev[key] = val
        if dev:
            return dev

class Bravia:
    """Navigate to: [Settings] → [Network] → [Home Network Setup] → [IP Control]
        Set [Authentication] to [Normal and Pre-Shared Key]
        There should be a new menu entry [Pre-Shared Key]. Set it for example to 0000.
    """

    def __init__(self, ip, macaddres=None, psk='0000', sid=None, model='Unknown'):
        self._data = dict()
        self.host = f'http://{ip}'
        self.ip = ip
        self.psk = psk
        self._data['cid'] = sid
        self._data['model'] = model
        self.commands = {}
        if macaddres is not None:
            self.mac = macaddres
        self._report_handelers = set()
        self.session = Session(f'http://{ip}/sony')
        self.session.add_header('X-Auth-PSK', self.psk)
        self.ircc_code = dict()
        self.cmd = {'set_power': self.set_power,
                    'button': self.send_ircc,
                    'set_source_uri': self.set_sources_uri}
        self._dev_init()
    
    def _dev_init(self):
        if self.power:
            self.ircc_code = self.get_all_commands()
            self._data.update(self.get_system_info())
    
    def device_status(self):
        _status = dict()
        if self.power:
            _status['power'] = 'on'
            _status.update(self.get_content_info())
        else:
            _status['power'] = 'off'
        return _status
    
    def write(self, data):
        _data = data.get('data', {}).copy()
        if not _data:
            raise ValueError('write: data is empty')
            return
        c, v = _data.popitem()
        if type(v) == dict:
            self.cmd.get(c, self._unknown)(**v)
        else:
            self.cmd.get(c, self._unknown)(v)
    
    def _unknown(self, value):
        raise ValueError(f'unknown parameter {value}')
    
    def add_report_handler(self, handler):
        self._report_handelers.add(handler)
        
    def _handle_events(self, event):
        for handler in self._report_handelers:
            handler(event)
    
    def refresh_status(self):
        data = self.get_content_info()
        if data:
            self._data.update(data)
            Thread(target=self._handle_events,
                   args=({'cmd': 'report', 'sid': self.sid, 'model': self.model, 'data': data},)).start()
        
    @property
    def power(self):
        """This API provides the current power status of the device."""
        try:
            self.session.timeout = 2
            ret = self.session.post(path='system', data=self._cmd("getPowerStatus"))
        except socket.error:
            return False
        except Exception:
            return False
        
        if ret.code == 200:
            result = ret.json
            if 'result' in result:
                status = result['result'][0].get('status')
                if status == 'standby':
                    return False
                elif status == 'active':
                    return True
            elif 'error' in result:
                if result['error'][0] == 404:
                    # TV is probably booting at this point - so not available yet
                    return False
                elif result['error'][0] == 403:
                    # A 403 Forbidden is acceptable here, because it means the TV is responding to requests
                    return True
        else:
            # Uncaught error
            return False
    
    def set_power(self, status):
        """This API provides the function to change the current power status of the device.
        The power set on True is supported only in “Sleep” mode.
        If the Remote start setting (Settings - Network) is OFF, an error is received form the client when setting power = True."""
        st = {'on': self.on, 'off': self.off}.get(status)
        if st is None:
            raise ValueError(f'Argument status need to by one of [on , off]')
        else:
            st()
    
    def get_supported_api(self):
        """This API provides the supported services and their information"""
        
        return self._get('guide', 'getSupportedApiInfo', [{"services": []}])
    
    def get_interface_information(self):
        """This API provides information of the REST API interface provided by the server. This API must not include private information."""
        return self._get('system', 'getInterfaceInformation')
    
    def get_system_info(self):
        """This API provides general information on the device."""
        
        ret = self.session.post(path='system',
                                data=self._cmd('getSystemInformation'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_connected_sources(self):
        """This API provides information on the current status of all external input sources of the device."""
        
        ret = self.session.post(path='avContent',
                                data=self._cmd('getCurrentExternalInputsStatus'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_application_list(self):
        """This API provides the list of applications that can be launched by setActiveApp"""
        
        ret = self.session.post(path='appControl',
                                data=self._cmd('getApplicationList'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_application_status(self):
        """This API provides the status of the application itself or the accompanying status related to a specific application."""
        
        ret = self.session.post(path='appControl',
                                data=self._cmd('getApplicationStatusList'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_content_info(self):
        """This API provides information of the currently playing content or the currently selected input."""
        ret = self.session.post(path='avContent',
                                data=self._cmd('getPlayingContentInfo'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_sources(self):
        """This API provides the list of sources in the scheme."""
        ret = self.session.post(path='avContent',
                                data=self._cmd('getSourceList', params=[{"scheme": "extInput"}]))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def set_sources(self, exinput, extype='tuner', port='1', trip='', srv=''):
        """This API provides the list of sources in the scheme."""
        ext = {'hdmi': f'extInput:hdmi?port={port}',
               'component': f'extInput:component?port={port}',
               'widi': f'extInput:widi?port={port}',
               'cec': f'extInput:cec?type={extype}&port={port}',
               'tv': f'tv:dvbt?trip={trip}&srvName={srv}'}.get(exinput)
        if ext is None:
            raise ValueError(f'Incorrect input {exinput}')
        ret = self.session.post(path='avContent',
                                data=self._cmd('setPlayContent', params=[{"uri": f"{ext}"}]))
        if ret.code == 200:
            return self._parse_result(ret.json)
        
    def set_sources_uri(self, uri):
        ret = self.session.post(path='avContent',
                                data=self._cmd('setPlayContent', params=[{"uri": f"{uri}"}]))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_sound_settings(self, target=''):
        """This API provides the current settings and supported settings related to the sound configuration items."""
        
        ret = self.session.post(path='audio',
                                data=self._cmd('getSoundSettings', params=[{'target': f'{target}'}], version='1.0'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def get_speaker_settings(self):
        """TThis API provides current settings and supported settings related to speaker configuration items."""
        
        ret = self.session.post(path='audio',
                                data=self._cmd('getSpeakerSettings', params=[{'target': ''}]))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def set_mute(self, status):
        """This API provides the function to change the audio mute status.
        
        Args:
            status (bool)"""
        if type(status) is not bool:
            raise ValueError
        ret = self.session.post(path='audio',
                                data=self._cmd('setAudioMute', params=[{"status": status}]))
    
    def get_volume(self):
        ret = self.session.post(path='audio',
                                data=self._cmd('getVolumeInformation'))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def set_volume(self, value, target=''):
        print('set volume')
        ret = self.session.post(path='audio',
                          data=self._cmd('setAudioVolume', params=[{"volume": f'{value}',"target": target}], pid=666))
        print(ret.json)

    def get_all_commands(self):
        ret = self.session.post(path='system', data=self._cmd('getRemoteControllerInfo'))
        try:
            result = ret.json['result'][1]
            commands = dict()
            for func in result:
                if 'name' in func:
                    commands[func.get('name')] = func.get('value')
        except:
            return {}
        return commands
    
    def send_ircc(self, name):
        """Send command codes of IR remote. (InfraRed Compatible Control over Internet Protocol)
        
        Args:
            name (str): name of command to send
        """
        try:
            if not self.ircc_code:
                self.ircc_code = self.get_all_commands()
            code = self.ircc_code.get(name)
        except AttributeError:
            raise BraviaError(messeage=f'Ircc name not recognize {name}')
        
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
        self.session.post(path='IRCC', headers=headers, raw=data)
        self.refresh_status()

    @staticmethod
    def _cmd(cmd, params=[], pid=10, version='1.0'):
        return {'method': cmd, 'params': params, 'id': pid, 'version': version}

    def _get(self, path, cmd, params=[]):
        ret = self.session.post(path=path,
                                data=self._cmd(cmd, params))
        if ret.code == 200:
            return self._parse_result(ret.json)
        
    def on(self):
        """Power on tv"""
        mac = self.mac.replace(":", "")
        data = b'FFFFFFFFFFFF' + (mac * 20).encode()
        send_data = b''

        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
            send_data += struct.pack('B', int(data[i: i + 2], 16))
        
        # Broadcast it to the LAN.
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(send_data, ('255.255.255.255', 7))
     
    def off(self):
        """Power off tv"""
        ret = self.session.post(path='system',
                                data=self._cmd('setPowerStatus', params=[{"status": False}]))
        if ret.code == 200:
            return self._parse_result(ret.json)
    
    def _parse_result(self, msg):
        # print(f'debug: {msg} {type(msg)}')
        if type(msg) == dict:
            if 'error' in msg:
                raise BraviaError(msg['error'])
            elif 'result' in msg and msg['result']:
                return msg['result'][0]
    
    @property
    def sid(self):
        return self._data.get('cid', '')

    @property
    def model(self):
        return self._data.get('model', '')

    @property
    def mac(self):
        return self._data.get('macAddr', '')

    @mac.setter
    def mac(self, val):
        if len(val) == 17:
            self._data['macAddr'] = val
        else:
            raise ValueError('Incorrect MAC address format')


class BraviaError(Exception):
    _codes = {
        2: 'Timeout',
        3: 'Illegal Argument',
        5: 'Illegal Request',
        12: 'No Such Method',
        14: 'Unsupported Version'
        }
    
    def __init__(self, code=[], messeage=f'Unknow Error'):
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
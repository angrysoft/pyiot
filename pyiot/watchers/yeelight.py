from . import WatcherBaseDriver
# from pyiot.xiaomi.yeelight import YeelightDev
import socket
import json

class YeelightWatcher(WatcherBaseDriver):
    def __init__(self, dev):
        self.connection = socket.create_connection((dev.status.ip, dev.status.port))
        self.reader = self.connection.makefile()
        self._loop = True
        self.dev = dev
        
    def watch(self, handler):
        while self._loop:
            _data = dict()
            try:
                jdata = json.loads(self.reader.readline())
            except json.JSONDecodeError as err:
                print(err)
                continue
            
            if 'params' in jdata:
                if 'ct' in jdata['params']:
                    jdata['params']['ct_pc'] = self._ct2pc(int(jdata['params']['ct']))
                handler({'cmd': 'report',
                         'sid': self.dev.status.sid,
                         'model': self.dev.status.model,
                         'data': jdata['params'].copy()})
                # handler(jdata['params'].copy())
    
    def _ct2pc(self, value:int ) -> int :
        return int(100 - (self.dev.max_ct - value) / (self.dev.max_ct-self.dev.min_ct) * 100)
        
                
    def stop(self):
        self._loop = False
        self.reader.close()
        self.connection.close()  
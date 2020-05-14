from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import json
import socket
from threading import Thread, Event, RLock


class EwelinkWatcher(WatcherBaseDriver):
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, "_ewelink._tcp.local.", self)
        self._loop = True
        self._handler = None
        self.ev = Event()
    
    def watch(self, handler):
        self._handler = handler
        self.ev.wait()
        self.zeroconf.close()
            
    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        # info = zeroconf.get_service_info(type, name)
        pass
    
    def update_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if self._handler is not None:
            self._handler(self._parse(info.properties))
    
    def _parse(self, prop):
        ret = {}
        if b'data1' in prop:
            ret = {'id': prop[b'id'].decode(), 'model': prop[b'type'].decode(), 'data': json.loads(prop[b'data1'])}
        return ret

    def stop(self):
        self.ev.set()
        

class Discover:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.zeroconf = Zeroconf()
        self.browser = None
        self.searching = Event()
        self.sid = None
        self._devices = dict()
        
    def search(self, sid=None):
        self.searching.clear()
        if sid:
            self.sid = sid
        self.browser = ServiceBrowser(self.zeroconf, "_ewelink._tcp.local.", handlers=[self._add_service])
        self.searching.wait(self.timeout)
        self.zeroconf.close()
        return self._devices
        
    def _add_service(self, zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
         if state_change is ServiceStateChange.Added:
            info = self._parse(zeroconf.get_service_info(service_type, name))
            if info:
                if self.sid == info['id']: 
                    self._devices = info
                    self.searching.set()
                else:
                    self._devices[info['id']] = info

    def _parse(self, info):
        ret = {}
        props = info.properties
        if b'data1' in props:
            try:
                ret = {'id': props[b'id'].decode(), 'model': props[b'type'].decode(),
                       'ip': socket.inet_ntoa(info.addresses[0]), 'port': info.port,
                       'data': json.loads(props[b'data1'])}
            except IndexError:
                pass
        return ret
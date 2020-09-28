from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
import json
import socket
from threading import Thread, Event, RLock
from pyiot.watcher import WatcherBaseDriver


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
        
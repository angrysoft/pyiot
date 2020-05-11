
from urllib.parse import quote
from urllib.request import urlopen, Request
import urllib.error
from base64 import b64encode
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
from time import sleep
import json
import socket
from threading import Thread, Event, RLock

class SessionError(Exception):
    pass

class Response:
    def __init__(self, resp):
        self.resp = resp
        self._headers = {}
        if resp.readable:
            self.body = resp.read()
            self._headers = resp.headers

    @property
    def code(self):
        return self.resp.code

    @property
    def status(self):
        return self.resp.status

    @property
    def json(self):
        try:
            msg = json.loads(self.body)
            dev_data = msg.get('data')
            if type(dev_data) == str:
                dev_data = json.loads(dev_data)
                msg['data'] = dev_data
            return msg
        except json.JSONDecodeError:
            raise SessionError(self.body)

    @property
    def headers(self):
        return self.resp.headers

class Session:
    def __init__(self, url, port, timeout=5):
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.url = f'{url}:{port}'
        self.port = port
        self.timeout = timeout
        self.lock = RLock()
        
    def post(self, path='', data=None, headers={}, query={}):
        return self.request(path, method='POST', data=data, headers=headers, query=query)

    def request(self, path, method='GET', data=None, headers={}, query={}):
        headers.update(self.headers)
        _query = '&'.join([f'{q}={query[q]}' for q in query])
        if data is not None and type(data) is not str:
            try:
                data = json.dumps(data)
            except json.JSONDecodeError:
                raise SessionError(f'params parsing error {data}')
            data = data.encode('utf8')
        if query:
            _query = f'?{_query}'  
        req = Request(url=f'{self.url}/{quote(path)}{_query}', method=method, data=data, headers=headers)
        with self.lock:    
            try:
                return Response(urlopen(req))
            except urllib.error.HTTPError as err:
                return Response(err)
            
class WatcherBaseDriver:
    def watch(self, handeler):
        pass
    
    def stop(self):
        pass    

    
class Watcher:
    def __init__(self, driver=None):
        self._report_handlers = set()
        if isinstance(driver, WatcherBaseDriver):
            Thread(target=driver.watch, args=(self._handler,), daemon=True).start()
            
    def _handler(self, msg: dict) -> None:
        Thread(target=self._handle_events, args=(msg,)).start()
    
    def add_report_handler(self, handler):
        self._report_handlers.add(handler)
    
    def _handle_events(self, event):
        for handler in self._report_handlers:
            handler(event)

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
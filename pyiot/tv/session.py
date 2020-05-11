from urllib.parse import quote
from urllib.request import urlopen, Request
import urllib.error
import socket
from base64 import b64encode
import json

class Session:
    def __init__(self, url, port=None, ssl=None, timeout=5, user=None, password=None):
        if user and password:
            pass
        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if port:
            self.url = f'{url}:{port}'
        else:
            self.url = url
        self.port = port
        self._timeout = timeout
        self.ssl = ssl
        self.user = user
        self.password = password
        # self.errors_retryable = (errno.EPIPE, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
        #                          errno.ECONNABORTED, errno.EHOSTDOWN, errno.EHOSTUNREACH,
        #                          errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN)
    
        if self.user and self.password:
            self._headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
    
    @property
    def timeout(self):
        return self._timeout
    
    @timeout.setter
    def timeout(self, value):
        self._timeout = value
    
    @property
    def headers(self):
        return self._headers
    
    def add_header(self, key, value):
        self._headers[key] = value 
    
    def get(self, path='', query={}):
        return self.request(method='GET', path=path, query=query)

    def post(self, path='', data=None, raw=None, headers={}, query={}):
        return self.request(path, method='POST', data=data, raw=raw, headers=headers, query=query)

    def put(self, path='', data=None, headers={}, query={}):
        return self.request(path, method='PUT', data=data, headers=headers, query=query)

    def delete(self, path, query={}):
        return self.request(path, method='DELETE', query=query)

    def head(self, path, query={}):
        return self.request(path, method='HEAD', query=query)

    def request(self, path, method='GET', data=None, raw=None, headers={}, query={}):
        headers.update(self.headers)
        _query = '&'.join([f'{q}={query[q]}' for q in query])
        if raw:
            data = raw.encode('utf8')
        elif data is not None and type(data) is not str:
            try:
                data = json.dumps(data)
            except json.JSONDecodeError:
                raise ValueError(f'params parsing error {data}')
            data = data.encode('utf8')
        if query:
            _query = f'?{_query}'
        
        req = Request(url=f'{self.url}/{quote(path)}{_query}', method=method, data=data, headers=headers)  
        try:
            return Response(urlopen(req, timeout=self.timeout))
        except urllib.error.HTTPError as err:
            return Response(err)
        except urllib.error.URLError as err:
            return TimeoutError(err)

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
            return json.loads(self.body)
        except json.JSONDecodeError:
            raise ValueError(self.body)

    @property
    def headers(self):
        return self.resp.headers
    
class TimeoutError:
    def __init__(self, msg):
        self.code = 408
        self.reason = msg
        
    
from __future__ import annotations
from typing import Any, Dict
from urllib.parse import quote
from urllib.request import urlopen, Request
import urllib.error
from base64 import b64encode
import json

class HttpConnection:
    def __init__(self, url: str, port:int=0, timeout:int = 5, user:str = '', password: str = ''):
        self._headers:Dict[str,str] = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if port > 0:
            self.url = f'{url}:{port}'
        else:
            self.url = url
        self.port = port
        self._timeout: int = timeout
        self.user = user
        self.password = password
        # self.errors_retryable = (errno.EPIPE, errno.ETIMEDOUT, errno.ECONNRESET, errno.ECONNREFUSED,
        #                          errno.ECONNABORTED, errno.EHOSTDOWN, errno.EHOSTUNREACH,
        #                          errno.ENETRESET, errno.ENETUNREACH, errno.ENETDOWN)
    
        if self.user and self.password:
            self._headers['Authorization'] = f"Basic {b64encode(f'{self.user}:{self.password}'.encode('utf-8')).decode('ascii')}"
    
    @property
    def timeout(self) -> int:
        return self._timeout
    
    @timeout.setter
    def timeout(self, value:int):
        self._timeout = value
    
    @property
    def headers(self) -> Dict[str,str]:
        return self._headers
    
    def add_header(self, key:str, value:str):
        self._headers[key] = value 
    
    def get(self, path:str='', query: Dict[str,str]={}) -> Response:
        return self.request(method='GET', path=path, query=query)

    def post(self, path:str='', data:Dict[str,Any]={}, raw:str='', headers:Dict[str,str]={}, query:Dict[str,str]={}) -> Response:
        return self.request(path, method='POST', data=data, raw=raw, headers=headers, query=query)

    def put(self, path:str='', data:Dict[str,Any]={}, raw:str='', headers:Dict[str,str]={}, query:Dict[str,str]={}) -> Response:
        return self.request(path, method='PUT', data=data, headers=headers, query=query)

    def delete(self, path:str='', query:Dict[str,str]={}) -> Response:
        return self.request(path, method='DELETE', query=query)

    def head(self, path:str='', query:Dict[str,str]={}) -> Response:
        return self.request(path, method='HEAD', query=query)

    def request(self, path:str, method:str='GET', data:Dict[str,Any]={}, raw:str='', headers:Dict[str,str]={}, query:Dict[str,str]={}) -> Response:
        headers.update(self.headers)
        _query = '&'.join([f'{q}={query[q]}' for q in query])
        if raw:
            _data:str = raw
        elif data and type(data) is not str:
            try:
                _data:str = json.dumps(data)
            except json.JSONDecodeError:
                raise ValueError(f'params parsing error {data}')
        else:
            _data:str = ''
                
        if query:
            _query = f'?{_query}'
        
        req = Request(url=f'{self.url}/{quote(path)}{_query}', method=method, data=_data.encode('utf8'), headers=headers)  
        try:
            return Response(urlopen(req, timeout=self.timeout))
        except urllib.error.HTTPError as err:
            return Response(err)
        except urllib.error.URLError as err:
            # return TimeoutError(err)
            return Response(err)

class Response:
    def __init__(self, resp:Any):
        self.resp = resp
        self._headers = {}
        self.body = ''
        if hasattr(resp, 'readable'):
            self.body = resp.read()
            self._headers = resp.headers

    @property
    def code(self) -> int:
        return self.resp.code

    @property
    def status(self):
        return self.resp.status

    @property
    def json(self) -> Dict[str, Any]:
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
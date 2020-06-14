class BaseDeviceInterface:
    def __init__(self, sid):
        self._data = dict()
        self._data["sid"] = sid
        self.cmd = dict()
    
    def heartbeat(self, data):
        self.report(data)
    
    def report(self, data:dict) -> None:
        _data = data.copy()
        self._data.update(_data.pop('data', {}))
        self._data.update(_data)
    
    
    @property
    def sid(self):
        return self._data.get("sid")
    
    @property
    def name(self):
        return self._data.get('name', "")
    
    @name.setter
    def name(self, value):
        self._data['name'] = value
    
    @property
    def place(self):
        return self._data.get('place', "")
    
    @place.setter
    def place(self, value):
        self._data['place'] = value
    
    @property
    def model(self):
        return self._data.get('model', 'unknown')
    
    def device_status(self) -> dict:
        return {"sid": self.sid, "name": self.name, "place": self.place}
    
    def sync(self) -> dict:
        pass
    
    def query(self, *params) ->dict:
        pass
    
    def execute(self, command: dict) -> None:
        pass
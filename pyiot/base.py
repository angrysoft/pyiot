class BaseDeviceInterface:
    def __init__(self, sid):
        self._data = dict()
        self._data["sid"] = sid
        self.cmd = dict()
    
    def report(self, data:dict) -> None:
        self._data.update(data.pop('data', {}))
        self._data.update(data)
    
    def write(self, data):
        _data = data.get('data', {}).copy()
        if not _data:
            # raise ValueError('data is empty')
            return
        c, v = _data.popitem()
        if type(v) == dict:
            self.cmd.get(c, self._unknown)(**v)
        else:
            self.cmd.get(c, self._unknown)(v)
    
    def _unknown(self, *args):
        pass
    
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
    
    def device_status(self) -> dict:
        return {"sid": self.sid, "name": self.name, "place": self.place}
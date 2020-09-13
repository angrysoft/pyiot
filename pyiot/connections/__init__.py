class IdGen:
    def __init__(self, _max:int = 1000) -> None:
        self._current_id: int = 1
        self._last_id: int = 1
        self._maximum: int = _max
    
    
    def get_next_id(self) -> int:
        self._last_id = self._current_id
        self._current_id += 1
        if self._current_id > self._maximum:
                self._current_id = 1
        return self._current_id
    
    @property
    def current_id(self) -> int:
        return self._current_id
    
    @property
    def last_id(self) -> int:
        return self._last_id
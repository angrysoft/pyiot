from __future__ import annotations
from datetime import datetime


class Time:
    def __init__(self, hour: int = 0, minute: int = 0, seconds: int = 0) -> None:
        self._hour: int = hour
        self._minute: int = minute
        self._seconds: int = seconds

    def set_now(self):
        _date = datetime.now()
        self._hour = _date.hour
        self._minute = _date.minute
        self._seconds = _date.second

    @staticmethod
    def get_time_now():
        result = Time()
        result.set_now()
        return result

    @property
    def hour(self) -> int:
        return self._hour

    @property
    def minute(self) -> int:
        return self._minute

    @property
    def seconds(self) -> int:
        return self._seconds

    def __eq__(self, value: Time) -> bool:
        return (
            self._hour == value.hour
            and self._minute == value.minute
            and self._seconds == value.seconds
        )

    def __lt__(self, value: Time) -> bool:
        _local_sec = self._seconds + self._minute * 60 + self._hour * 3600
        _in_sec = value.seconds + value.minute * 60 + value.hour * 3600
        return _local_sec < _in_sec

    def __le__(self, value: Time) -> bool:
        return self.__eq__(value) or self.__lt__(value)

    def __gt__(self, value: Time) -> bool:
        _local_sec = self._seconds + self._minute * 60 + self._hour * 3600
        _in_sec = value.seconds + value.minute * 60 + value.hour * 3600
        return _local_sec > _in_sec

    def __ge__(self, value: Time) -> bool:
        return self.__eq__(value) or self.__gt__(value)

    def __repr__(self) -> str:
        return f"{self._hour:02}:{self._minute:02}:{self._seconds:02}"

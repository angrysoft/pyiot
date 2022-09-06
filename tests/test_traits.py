import unittest
from pyiot.traits import *
from pyiot import BaseDevice


class Dev(BaseDevice, MultiSwitch):
    def __init__(self) -> None:
        self.status.switches = ["left", "right"]

    def on(self, switch_name: str):
        pass

    def off(self, switch_name: str):
        pass

    def is_off(self, switch_name: str) -> bool:
        return True

    def is_on(self, switch_name: str) -> bool:
        return True


class TestTraits(unittest.TestCase):
    def test_class_instace(self):
        c = Dev("ccccc")
        d = Dev("ddddd")
        print(c.status.switches)
        print(d.status.switches)

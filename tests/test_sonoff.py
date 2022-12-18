#!/usr/bin/python

from pyiot.sonoff import Mini, PowerState
from time import sleep
import unittest

sid = "1000b6063e"
# sid = "1000b6e1c8"


class TestSonoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = Mini(sid)

    def test_a_set_power(self):
        wait_for_status = 2
        self.dev.on()
        sleep(wait_for_status)
        print(f"set on: is {self.dev.status.power} expected on")
        self.assertTrue(self.dev.is_on())
        sleep(wait_for_status)
        self.dev.off()
        sleep(wait_for_status)
        print(f"set off: is {self.dev.status.power} expected off")
        self.assertTrue(self.dev.is_off())

        self.dev.execute("on")
        sleep(wait_for_status)
        print(f"execute on: is {self.dev.status.power} expected on")
        self.assertTrue(self.dev.is_on())

        self.dev.execute("off")
        sleep(wait_for_status)
        print(f"execute off: is {self.dev.status.power} expected off")
        self.assertTrue(self.dev.is_off())

    def test_c_power(self):
        self.assertIn(self.dev.status.power, ["on", "off"])

    def test_c_pulse(self):
        self.assertIn(self.dev.status.pulse, ["on", "off"])

    def test_c_puslse_width(self):
        self.assertIsInstance(self.dev.status.pulseWidth, int)

    def test_d_set_power_on_state(self):
        self.dev.set_power_on_state(PowerState.OFF)
        sleep(1)
        self.assertIn(self.dev.status.startup, ["on", "off", "stay"])

    def test_e_device_status(self):
        self.assertIsInstance(self.dev.device_status(), dict)

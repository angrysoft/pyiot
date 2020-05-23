#!/usr/bin/python

from pyiot.sonoff import Mini, PowerState
from time import sleep
import unittest

sid = '1000b6063e'
# sid = "1000b6e1c8"

class TestSonoff(unittest.TestCase):
      @classmethod
      def setUpClass(cls):
            cls.dev = Mini(sid)
      
      def test_a_set_power(self):
            self.dev.on()
            sleep(1)
            self.assertTrue(self.dev.is_on())
            self.dev.off()
            sleep(1)
            self.assertTrue(self.dev.is_off())
            sleep(1)
            self.dev.set_power('on')
            sleep(1)
            self.assertTrue(self.dev.is_on())
            self.dev.write({'data':{'status': 'off'}})
            sleep(1)
            self.assertTrue(self.dev.is_off())
            
      def test_c_power(self):
            self.assertIn(self.dev.power, ['on', 'off'])
      
      def test_c_pulse(self):
            self.assertIn(self.dev.pulse, ['on', 'off'])
      
      def test_c_puslse_width(self):
            self.assertIsInstance(self.dev.pulse_width, int)
      
      def test_d_set_power_on_state(self):
            self.dev.set_power_on_state(PowerState.OFF)
            sleep(1)
            self.assertIn(self.dev.startup, ['on', 'off', 'stay'])

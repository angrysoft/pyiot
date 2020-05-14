#!/usr/bin/python

from pysonoff import *
from time import sleep
import unittest

sid = '1000b6063e'

class TestSonoff(unittest.TestCase):
      @classmethod
      def setUpClass(cls):
            cls.dev = Mini(sid)
      
      def test_a_on(self):
            self.dev.on()
            sleep(0.5)
            self.assertTrue(self.dev.is_on())
      
      def test_z_off(self):
            self.dev.off()
            sleep(0.5)
            self.assertTrue(self.dev.is_off())
            
      def test_c_power(self):
            self.assertIn(self.dev.power, ['on', 'off'])
      
      def test_c_startup(self):
            pass
      
      def test_c_pulse(self):
            self.assertIn(self.dev.pulse, ['on', 'off'])
      
      def test_c_puslse_width(self):
            pass
      
      def test_c_ssid(self):
            pass
      
      def test_d_set_power_on_state(self):
            self.dev.set_power_on_state(PowerState.OFF)
            sleep(0.5)
            self.assertIn(self.dev.startup, ['on', 'off', 'stay'])

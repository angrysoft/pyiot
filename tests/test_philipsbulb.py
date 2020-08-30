from time import sleep
import unittest
import os
from pyiot.xiaomi.philips_bulb import PhilipsBulb


sid = '235444403'

class TestPhilipsBulb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get('PHTOKEN')
        cls.dev = PhilipsBulb(token=token, sid=sid)
        # cls.dev.watcher.add_report_handler(print)
    
    def test_a_power_on(self):
        self.dev.on()
        sleep(1)
        self.assertTrue(self.dev.is_on())
    
    def test_d_ct_pc(self):
        sleep(0.5)
        self.dev.set_ct_pc(50)
        sleep(0.8)
        self.assertEqual(self.dev.ct_pc, 50)
    
    def test_f_bright(self):
        self.dev.set_bright(40)
        sleep(0.8)
        self.assertEqual(self.dev.bright, 40)
    
    def test_g_device_status(self):
        ret = self.dev.device_status()
        self.assertIsInstance(ret, dict)
    
    def test_z_power_off(self):
        self.dev.off()
        sleep(1)
        self.assertTrue(self.dev.is_off())
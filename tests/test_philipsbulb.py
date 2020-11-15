from time import sleep
import unittest
import os
from pyiot.xiaomi.philips_light import Candle

sid = '235444403'

class TestPhilipsBulb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = str(os.environ.get('PHTOKEN'))
        cls.dev = Candle(token=token, sid=sid)
        cls.dev.watcher.add_report_handler(print)
    
    # @unittest.skip('temp')
    def test_info(self):
        print(self.dev.status.power)
        info = self.dev.info()
        print(info)
        
    # @unittest.skip('temp')
    def test_a_onoff(self):
        self.dev.on()
        sleep(1)
        self.assertTrue(self.dev.is_on())
        self.dev.off()
        sleep(1)
        self.assertTrue(self.dev.is_off())
        sleep(1)
    
    # @unittest.skip('temp')
    def test_d_ct_pc(self):
        self.dev.set_ct_pc(50)
        sleep(0.8)
        self.assertEqual(self.dev.status.ct_pc, 50)
    
    # @unittest.skip('temp')
    def test_f_bright(self):
        self.dev.set_bright(40)
        sleep(0.8)
        self.assertEqual(self.dev.status.bright, 40)
    
    # @unittest.skip('temp')
    def test_g_device_status(self):
        ret = self.dev.device_status()
        self.assertIsInstance(ret, dict)
    
    # @unittest.skip('temp')
    def test_z_power_off(self):
        self.dev.off()
        sleep(1)
        self.assertTrue(self.dev.is_off())
from time import sleep
import unittest
from pyiot.xiaomi.yeelight import Color


sid = '0x0000000007e7bae0'
# sid = '0x000000000545b741'

class TestColor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = Color(sid)
        cls.dev.watcher.add_report_handler(print)
    
    def test_a_power(self):
        self.dev.on()
        sleep(0.5)
        self.assertTrue(self.dev.is_on())
        self.dev.off()
        sleep(0.5)
        self.assertTrue(self.dev.is_off())
        sleep(1)
        self.dev.set_power('on')
        sleep(0.5)
        self.assertTrue(self.dev.is_on())
    
    def test_b_rgb(self):
        sleep(0.5)
        self.dev.set_rgb(red=255)
        sleep(0.8)
        self.assertEqual(self.dev.rgb, 16711680)
        
        self.dev.set_rgb(green=255)
        sleep(0.8)
        self.assertEqual(self.dev.rgb, 65280)
        
        self.dev.set_rgb(blue=255)
        sleep(0.8)
        self.assertEqual(self.dev.rgb, 255)
        
        self.dev.set_color(16711680)
        sleep(0.8)
        self.assertEqual(self.dev.rgb, 16711680)
    
    def test_c_ct(self):
        sleep(0.5)
        self.dev.set_ct_abx(6000)
        sleep(0.8)
        self.assertEqual(self.dev.ct, 6000)
        self.dev.adjust_ct(-10)
        sleep(0.8)
        self.assertEqual(self.dev.ct, 5400)
    
    def test_d_ct_pc(self):
        sleep(0.5)
        self.dev.set_ct_pc(50)
        sleep(0.8)
        self.assertEqual(self.dev.ct_pc, 50)
    
    def test_f_bright(self):
        self.dev.set_bright(40)
        sleep(0.8)
        self.assertEqual(self.dev.bright, 40)
        self.dev.adjust_bright(-10)
        sleep(0.8)
        self.assertEqual(self.dev.bright, 30)
    
    def test_g_device_status(self):
        ret = self.dev.device_status()
        self.assertIsInstance(ret, dict)
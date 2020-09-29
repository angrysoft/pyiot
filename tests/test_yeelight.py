from time import sleep
import unittest
from pyiot.xiaomi.yeelight import Color, YeelightDev


sid = '0x0000000007e7bae0'
# sid = '0x000000000545b741'
# sid = '0x0000000007200259'

class TestColor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dev = Color(sid)
        # cls.dev.watcher.add_report_handler(print)
    
    def test_a_power(self):
        # sleep(1)
        self.dev.on()
        sleep(0.5)
        self.assertTrue(self.dev.is_on())
        sleep(1)
        self.dev.off()
        sleep(0.5)
        self.assertTrue(self.dev.is_off())
        sleep(1)
        self.dev.execute('on')
        sleep(0.5)
        self.assertTrue(self.dev.is_on())
        
    def test_a_get_props(self):
        ret = self.dev.get_prop(['power',
                                 'bright',
                                 'ct',
                                 'rgb',
                                 'hue',
                                 'sat',
                                 'color_mode',
                                 'flowing',
                                 'delayoff',
                                 'flow_params',
                                 'musing_on',
                                 'name',
                                 'bg_power',
                                 'bg_flowing',
                                 'bg_flow_params',
                                 'bg_ct',
                                 'bg_mode',
                                 'bg_bright',
                                 'bg_rgb',
                                 'bg_hue',
                                 'bg_sat',
                                 'nl_br',
                                 'active_mode'])
        print(ret)
        self.assertIsInstance(ret, dict)
    
    def test_b_rgb(self):
        sleep(0.5)
        self.dev.set_rgb(red=255)
        sleep(0.8)
        self.assertEqual(self.dev.status.rgb, 16711680)
        
        self.dev.set_rgb(green=255)
        sleep(0.8)
        self.assertEqual(self.dev.status.rgb, 65280)
        
        self.dev.set_rgb(blue=255)
        sleep(0.8)
        self.assertEqual(self.dev.status.rgb, 255)
        
        self.dev.set_color(16711680)
        sleep(0.8)
        self.assertEqual(self.dev.status.rgb, 16711680)
    
    def test_b_hsv(self):
        self.dev.set_hsv(hue=0, sat=100)
        sleep(0.8)
        self.dev.set_hsv(hue=120, sat=100)
        sleep(0.8)
        self.dev.set_hsv(hue=240, sat=100)
        sleep(0.8)
        self.assertEqual(self.dev.status.hue, 240)
        self.assertEqual(self.dev.status.sat, 100)
        sleep(0.8)
    
    def test_c_ct(self):
        sleep(0.5)
        self.dev.set_ct_abx(6000)
        sleep(0.8)
        self.assertEqual(self.dev.status.ct, 6000)
        self.dev.adjust_ct(-10)
        sleep(0.8)
        self.assertEqual(self.dev.status.ct, 5400)
    
    def test_d_ct_pc(self):
        sleep(0.5)
        self.dev.set_ct_pc(50)
        sleep(0.8)
        self.assertEqual(self.dev.status.ct_pc, 50)
    
    def test_f_bright(self):
        self.dev.set_bright(40)
        sleep(0.8)
        self.assertEqual(self.dev.status.bright, 40)
        self.dev.adjust_bright(-10)
        sleep(0.8)
        self.assertEqual(self.dev.status.bright, 30)
    
    def test_g_device_status(self):
        ret = self.dev.device_status()
        print(ret)
        self.assertIsInstance(ret, dict)
from time import sleep
import unittest
import os
from pyiot.xiaomi import Gateway, CtrlNeutral, CtrlNeutral2

# sid = '0x000000000545b741'
ctrlNeural1 = '158d00024e2e5b'
ctrlNeural2 = '158d00029b1929'

class TestAqara(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        passwd = os.environ.get('GWPASSWD')
        cls.gw = Gateway(gwpasswd=passwd)
        cls.gw.watcher.add_report_handler(print)
    
    def test_a_gateway(self):
        token = self.gw.token
        self.gw.set_rgb(red=255)
        sleep(1)
        self.assertEqual(self.gw.rgb, 1694433280)
        self.gw.off_led()
        sleep(1)
        self.assertEqual(self.gw.rgb, 0)
        
    def test_b_CtrlNeural1(self):
        dev = CtrlNeutral(ctrlNeural1, gateway=self.gw)
        sleep(0.5)
        dev.channel_0.on()
        sleep(1)
        self.assertTrue(dev.channel_0.is_on())
        dev.channel_0.off()
        sleep(1)
        self.assertTrue(dev.channel_0.is_off())
    
    def test_c_CtrlNeural2(self):
        dev = CtrlNeutral2(ctrlNeural2, gateway=self.gw)
        sleep(0.5)
        dev.channel_0.on()
        sleep(1)
        self.assertTrue(dev.channel_0.is_on())
        dev.channel_0.off()
        sleep(1)
        self.assertTrue(dev.channel_0.is_off())
        sleep(0.5)
        dev.channel_1.on()
        sleep(1)
        self.assertTrue(dev.channel_1.is_on())
        dev.channel_1.off()
        sleep(1)
        self.assertTrue(dev.channel_1.is_off())
        
        

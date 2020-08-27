from time import sleep
import unittest
import os
from pyiot.xiaomi import GatewayInterface, CtrlNeutral, CtrlNeutral2 
# , Gateway

# sid = '0x000000000545b741'
ctrlNeural1 = '158d00024e2e5b'
ctrlNeural2 = '158d00029b1929'

class TestAqara(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        passwd = os.environ.get('GWPASSWD')
        cls.gw = GatewayInterface(gwpasswd=passwd)
        cls.gw.watcher.add_report_handler(print)
    
    # def test_a_gateway(self):
    #     token = self.gw.token
    #     self.gw.set_rgb(red=255)
    #     sleep(1)
    #     self.assertEqual(self.gw.rgb, 1694433280)
    #     self.gw.off_led()
    #     sleep(1)
    #     self.assertEqual(self.gw.rgb, 0)
        
    def test_b_CtrlNeural1(self):
        dev = CtrlNeutral(ctrlNeural1, gateway=self.gw)
        sleep(0.5)
        dev.on()
        sleep(1)
        self.assertTrue(dev.is_on())
        dev.off()
        sleep(1)
        self.assertTrue(dev.is_off())
    
    # def test_c_CtrlNeural2(self):
    #     dev = CtrlNeutral2(ctrlNeural2, gateway=self.gw)
    #     sleep(0.5)
    #     dev.on(0)
    #     sleep(1)
    #     self.assertTrue(dev.is_on(0))
    #     dev.off(0)
    #     sleep(1)
    #     self.assertTrue(dev.is_off(0))
    #     sleep(0.5)
    #     dev.on(1)
    #     sleep(1)
    #     self.assertTrue(dev.is_on(1))
    #     dev.off(1)
    #     sleep(1)
    #     self.assertTrue(dev.is_off(1))
        
        

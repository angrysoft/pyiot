from pyiot.xiaomi.aqara import  Plug
from pyiot.sonoff.zigbee import SNZB03
from time import sleep
import unittest
from pyiot.zigbee.zigbee2mqtt import Zigbee2mqttGateway


plug = '0x00158d000283b219'
sensor_motion = '0x00124b001cd609d8'



class TestZ2M(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agw = Zigbee2mqttGateway()
        cls.agw.watcher.add_report_handler(print)

    # @unittest.skip("demonstrating skipping")    
    def test_Plug(self):
        dev = Plug(plug, gateway=self.agw)
        print(dev.commands,dev.traits)
        sleep(0.5)
        dev.on()
        sleep(1)
        self.assertTrue(dev.is_on())
        dev.off()
        sleep(1)
        self.assertTrue(dev.is_off())
        dev.toggle()
        sleep(1)
        self.assertTrue(dev.is_on())
        dev.toggle()
        sleep(1)
        self.assertTrue(dev.is_off())
    
    def test_senosrmotion(self):
        dev = SNZB03(sensor_motion, gateway=self.agw)
        print(dev.device_status())
        input()
        
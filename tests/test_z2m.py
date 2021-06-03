from pyiot.xiaomi.aqara import Gateway, SensorHt, SensorMotionAq2, SensorSwitchAq2, CtrlNeutral, CtrlNeutral2, Plug, Switch, WeatherV1, Magnet
from pyiot.sonoff.zigbee import SNZB03
from time import sleep
import unittest
from pyiot.zigbee.zigbee2mqtt import Zigbee2mqttGateway


# plug = '0x00158d000283b219'
plug = '0x00158d00027d0065'
sensor_motion = '0x00124b001cd609d8'

ctrlNeural1 = '0x00158d00024e2e5b'
# ctrlNeural2 = '0x00158d00029b1929'
ctrlNeural2 = '0x00158d0002bffe5a'
plug = '0x00158d00027d0065'
switch = '0x00158d00033ef2d8'
sensor_switchaq2 = '0x00158d000200a020'
# sensor_switchaq2 = '0x00158d0002a18c2b'
sensor_ht = '0x00158d000208d668'
weatherv1 = '0x00158d0002e966b9'
magnet = '0x00158d0002a67612'
sensor_motionaq2 = '0x00158d0002ec03fe'

# class TestZ2M(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         cls.agw = Zigbee2mqttGateway(host='192.168.10.4', user='homedaemon', password='spyb0tk34s')
#         cls.agw.watcher.add_report_handler(print)

#     # @unittest.skip("demonstrating skipping")    
#     def test_Plug(self):
#         dev = Plug(plug, gateway=self.agw)
#         print(dev.commands,dev.traits)
#         sleep(0.5)
#         dev.on()
#         sleep(1)
#         self.assertTrue(dev.is_on())
#         dev.off()
#         sleep(1)
#         self.assertTrue(dev.is_off())
#         dev.toggle()
#         sleep(1)
#         self.assertTrue(dev.is_on())
#         dev.toggle()
#         sleep(1)
#         self.assertTrue(dev.is_off())
    
#     def test_senosrmotion(self):
#         dev = SNZB03(sensor_motion, gateway=self.agw)
#         print(dev.device_status())
#  

class TestAqara(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agw = Zigbee2mqttGateway(host='192.168.10.4', user='homedaemon', password='spyb0tk34s')
        cls.agw.watcher.add_report_handler(print)
    
        
    # @unittest.skip("demonstrating skipping")
    def test_CtrlNeural1(self):
        dev = CtrlNeutral(ctrlNeural1, gateway=self.agw)
        sleep(1)
        dev.on()
        sleep(1)
        print(dev.is_on())
        self.assertTrue(dev.is_on())
        dev.off()
        sleep(1)
        print(dev.is_off())
        self.assertTrue(dev.is_off())
        
    # @unittest.skip("demonstrating skipping")
    def test_CtrlNeural2(self):
        dev = CtrlNeutral2(ctrlNeural2, gateway=self.agw)
        # sleep(0.5)
        # dev1 = CtrlNeutral2(ctrlNeural2_1, gateway= self.agw)
        # sleep(0.5)

        # dev2 = CtrlNeutral2('0x00158d0002a18c2b', gateway= self.agw)
        # sleep(0.5)

        # for d in self.agw._subdevices:
        #     print(d, id(self.agw._subdevices[d].status))
        
        dev.on('left')
        sleep(1)
        self.assertTrue(dev.is_on('left'))
        dev.off('left')
        sleep(1)
        self.assertTrue(dev.is_off('left'))
        sleep(1)
        dev.on('right')
        sleep(1)
        self.assertTrue(dev.is_on('right'))
        dev.off('right')
        sleep(1)
        self.assertTrue(dev.is_off('right'))
    
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
    
    def test_sensorswitch(self):
        dev = SensorSwitchAq2(sensor_switchaq2, gateway=self.agw)
        print(dev.status())
    
    def test_switch(self):
        dev = Switch(switch, gateway=self.agw)
        print(self.agw.get_device(switch))
        print(dev.device_status())
        input()
    
    def test_sensorht(self):
        dev = SensorHt(sensor_ht, gateway=self.agw)
        
        print(dev.device_status())
    
    def test_weather(self):
        dev = WeatherV1(weatherv1, gateway=self.agw)
       
        print(dev.device_status())
    
    def test_magnet(self):
        dev = Magnet(magnet, gateway=self.agw)
        
        print(dev.device_status())
    
    def test_senosrmotion(self):
        dev = SensorMotionAq2(sensor_motionaq2, gateway=self.agw)
        print(dev.device_status())

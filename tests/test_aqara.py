from pyiot.xiaomi.aqara import Gateway, SensorHt, SensorMotionAq2, SensorSwitchAq2, CtrlNeutral, CtrlNeutral2, Plug, Switch, WeatherV1, Magnet
from time import sleep
import unittest
import os
from pyiot.zigbee.aqaragateway import AqaraGateway

# sid = '0x000000000545b741'
ctrlNeural1 = '158d00024e2e5b'
ctrlNeural2 = '158d00029b1929'
ctrlNeural2_1 = '158d0002bffe5a'
plug = '158d00027d0065'
switch = '158d00033ef2d8'
sensor_switchaq2 = '158d000200a020'
sensor_ht = '158d000208d668'
weatherv1 = '158d0002e966b9'
magnet = '158d0002a67612'
sensor_motionaq2 = '158d0002ec03fe'
gateway = '7c49eb17b2a0'


class TestAqara(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        passwd:str = os.environ.get('GWPASSWD', '')
        cls.agw = AqaraGateway(gwpasswd=passwd)
        cls.agw.watcher.add_report_handler(print)
    
    # @unittest.skip("demonstrating skipping")
    def test_a_gateway(self):
        dev = Gateway(gateway, self.agw)
        dev.set_rgb(red=255)
        sleep(1)
        self.assertEqual(dev.status.rgb, 1694433280)
        dev.set_color(0)
        sleep(1)
        self.assertEqual(dev.status.rgb, 0)
        
    # @unittest.skip("demonstrating skipping")
    def test_CtrlNeural1(self):
        dev = CtrlNeutral(ctrlNeural1, gateway=self.agw)
        print(dev.commands,dev.traits)
        sleep(0.5)
        dev.on()
        sleep(1)
        self.assertTrue(dev.is_on())
        dev.off()
        sleep(1)
        self.assertTrue(dev.is_off())
        
    # @unittest.skip("demonstrating skipping")
    def test_CtrlNeural2(self):
        dev = CtrlNeutral2(ctrlNeural2, gateway=self.agw)
        sleep(0.5)
        dev1 = CtrlNeutral2(ctrlNeural2_1, gateway= self.agw)
        sleep(0.5)

        dev2 = CtrlNeutral2('158d0002a18c2b', gateway= self.agw)
        sleep(0.5)

        for d in self.agw._subdevices:
            print(d, id(self.agw._subdevices[d].status))
        
        dev.on('left')
        sleep(1)
        self.assertTrue(dev.is_on('left'))
        dev.off('left')
        sleep(1)
        self.assertTrue(dev.is_off('left'))
        sleep(0.5)
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
        
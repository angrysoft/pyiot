from pyiot.xiaomi.aqara import SensorHt, SensorMotionAq2, SensorSwitchAq2,GatewayInterface, CtrlNeutral, CtrlNeutral2, Plug, Switch, WeatherV1, Magnet
from time import sleep
import unittest
import os

# sid = '0x000000000545b741'
ctrlNeural1 = '158d00024e2e5b'
ctrlNeural2 = '158d00029b1929'
plug = '158d00027d0065'
switch = '158d00033ef2d8'
sensor_switchaq2 = '158d000200a020'
sensor_ht = '158d000208d668'
weatherv1 = '158d0002e966b9'
magnet = '158d0002a67612'
sensor_motionaq2 = '158d0002ec03fe'


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
        
    @unittest.skip("demonstrating skipping")
    def test_CtrlNeural1(self):
        dev = CtrlNeutral(ctrlNeural1, gateway=self.gw)
        print(dev.commands,dev.traits)
        sleep(0.5)
        dev.on()
        sleep(1)
        self.assertTrue(dev.is_on())
        dev.off()
        sleep(1)
        self.assertTrue(dev.is_off())
        
    @unittest.skip("demonstrating skipping")
    def test_CtrlNeural2(self):
        dev = CtrlNeutral2(ctrlNeural2, gateway=self.gw)
        sleep(0.5)
        print(dev.commands,dev.traits, dev.switches(), dev.switch_no())
        dev.on(0)
        sleep(1)
        self.assertTrue(dev.is_on(0))
        dev.off(0)
        sleep(1)
        self.assertTrue(dev.is_off(0))
        sleep(0.5)
        dev.on(1)
        sleep(1)
        self.assertTrue(dev.is_on(1))
        dev.off(1)
        sleep(1)
        self.assertTrue(dev.is_off(1))
    
    @unittest.skip("demonstrating skipping")    
    def test_Plug(self):
        dev = Plug(plug, gateway=self.gw)
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
        dev = SensorSwitchAq2(sensor_switchaq2, gateway=self.gw)
        
        print(dev.status())
    
    def test_switch(self):
        dev = Switch(switch, gateway=self.gw)
        print(self.gw.read_device(switch))
        
        print(dev.device_status())
    
    def test_sensorht(self):
        dev = SensorHt(sensor_ht, gateway=self.gw)
        
        print(dev.device_status())
    
    def test_weather(self):
        dev = WeatherV1(weatherv1, gateway=self.gw)
       
        print(dev.device_status())
    
    def test_magnet(self):
        dev = Magnet(magnet, gateway=self.gw)
        
        print(dev.device_status())
    
    def test_senosrmotion(self):
        dev = SensorMotionAq2(sensor_motionaq2, gateway=self.gw)
        print(dev.device_status())
        
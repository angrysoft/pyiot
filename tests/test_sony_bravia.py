from time import sleep
import unittest
import os
from pyiot.sony import Bravia

class BraviaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tv = Bravia('192.168.10.5', macaddres='FC:F1:52:2A:9B:1E')
    
    def test_a_power(self):
        self.power = self.tv.power
        self.assertIsInstance(self.power, bool, msg=f'Tv power is {self.power}')
        
        self.tv.on()
        sleep(2)
        self.assertTrue(self.tv.power)
    
    def test_supported_apiinfo(self):
        ret = self.tv.supported_api()
        self.assertIsInstance(ret, dict, msg=ret)
    
    def test_application_list(self):
        ret = self.tv.application_list()
        self.assertIsInstance(ret, list, msg=ret)
    
    def test_application_status(self):
        ret = self.tv.application_status()
        self.assertIsInstance(ret, list, msg=ret)
    
    def test_content_info(self):
        ret = self.tv.content_info()
        self.assertIsInstance(ret, dict, msg=ret)
    
    # def test_sound_settings(self):
    #     print(self.tv.sound_settings())
    
    # def test_speaker_settings(self):
    #     print(self.tv.speaker_settings())
    
    # def test_sources(self):
    #     print(self.tv.sources())
    
    # def test_a_volume_set(self):
        # self.tv.set_volume('+50', target='speaker')
    
    # def test_b_volume(self):
    #     print(self.tv.get_volume())
    
    # def test_mute(self):
    #     self.tv.mute(False)
    
    #def test_set_source(self):
    #    self.tv.set_sources('cec', port=3)
    
    # def test_system_info(self):
    #     print(self.tv.system_info())
    
    # def test_send_ircc(self):
    #     self.tv.send_ircc('VolumeUp')
    
    # def test_write(self):
    #     self.tv.write({'data':{'button': 'VolumeDown'}})
    
    # def test_all_cmds(self):
    #     print(self.tv.get_all_commands())
    
    # def test_sources_list(self):
    #     for s in self.tv.connected_sources():
    #         print(s)
    
    def test_zz_off(self):
        self.tv.off()
        sleep(0.5)
        self.assertFalse(self.tv.power)
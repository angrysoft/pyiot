from time import sleep
import unittest
import os
from pyiot.sony import Bravia, BraviaError

class BraviaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tv = Bravia('192.168.10.5') # , macaddres='FC:F1:52:2A:9B:1E')
    
    def test_a_power(self):
        self.assertIsInstance(self.tv.is_on(), bool, msg=f'Tv power is {self.power}')
        self.tv.on()
        sleep(2)
        self.assertTrue(self.tv.status.is_on())
    
    def _cmd(self, cmd, *args):
        try:
            if args:
                ret = cmd(*args)
            else:
                ret = cmd()
                
        except BraviaError as err:
            if err.code_no == 12:
                self.skipTest(str(err))
            else:
                raise Exception(str(err))
        return ret
    
    def test_supported_apiinfo(self):
        ret = self._cmd(self.tv.get_supported_api)
        self.assertIsInstance(ret, list, msg=ret)
    
    def test_application_list(self):
        ret = self._cmd(self.tv.get_application_list)
        self.assertIsInstance(ret, list, msg=ret)
    
    def test_application_status(self):
        ret = self._cmd(self.tv.get_application_status)
        self.assertIsInstance(ret, list, msg=ret)
    
    def test_content_info(self):
        ret = self._cmd(self.tv.get_content_info)
        self.assertIsInstance(ret, dict, msg=ret)
    
    def test_sound_settings(self):
        ret = self._cmd(self.tv.get_sound_settings)
        self.assertIsInstance(ret, dict, msg=ret)
        
    def test_speaker_settings(self):
        ret = self._cmd(self.tv.get_speaker_settings)
        self.assertIsInstance(ret, dict, msg=ret)
    
    def test_sources(self):
        ret = self._cmd(self.tv.get_sources)
        self.assertIsInstance(ret, list, msg=ret)
    
    def test_a_volume_set(self):
        ret = self._cmd(self.tv.set_volume, '+50', 'speaker')
        print(ret, type(ret))
        self.assertIsInstance(ret, dict, msg=ret)
    
    # def test_b_volume(self):
    #     print(self.tv.get_volume())
    
    def test_mute(self):
        self.tv.set_mute(False)
    
    #def test_set_source(self):
    #    self.tv.set_sources('cec', port=3)
    
    # def test_system_info(self):
    #     print(self.tv.system_info())
    
    def test_send_ircc(self):
        self.tv.send_ircc('VolumeUp')
    
    
    
    # def test_all_cmds(self):
    #     print(self.tv.get_all_commands())
    
    # def test_sources_list(self):
    #     for s in self.tv.connected_sources():
    #         print(s)
    
    # def test_zz_off(self):
    #     self.tv.off()
    #     sleep(0.5)
    #     self.assertFalse(self.tv.power)
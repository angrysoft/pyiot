from pyiot.sony.bravia import BraviaApi, KDL48W585B, BraviaError
from time import sleep
import unittest
from typing import Any


class BraviaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tv = BraviaApi("192.168.10.5", mac="FC:F1:52:2A:9B:1E")

    def test_a_power(self):
        self.tv.on()
        sleep(2)
        self.assertTrue(self.tv.check_power_status())

    def _cmd(self, cmd, *args) -> Any:
        ret = {}
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

    def test_supported_function(self):
        ret = self._cmd(self.tv.get_supported_function)
        print(ret)
        self.assertIsInstance(ret, list, msg=ret)

    def test_interface_information(self):
        ret = self._cmd(self.tv.get_interface_information)
        print(ret)
        self.assertIsInstance(ret, dict, msg=ret)

    def test_application_list(self):
        ret = self._cmd(self.tv.get_application_list)
        self.assertIsInstance(ret, list, msg=ret)

    def test_application_status(self):
        ret = self._cmd(self.tv.get_application_status)
        self.assertIsInstance(ret, list, msg=ret)

    def test_content_info(self):
        ret = self._cmd(self.tv.get_content_info)
        print(ret)
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
        self._cmd(self.tv.set_volume, "+50", "speaker")

    def test_b_volume(self):
        print(self.tv.get_volume())

    def test_mute(self):
        self.tv.set_mute(True)
        print("mute")
        sleep(4)
        self.tv.set_mute(False)
        print("unmute")

    def test_power_saving(self):
        ret = self._cmd(self.tv.get_power_saving_mode)
        print(ret)
        self.tv.set_power_saving_mode("pictureOff")
        sleep(3)
        ret = self._cmd(self.tv.get_power_saving_mode)
        print(ret)
        self.tv.set_power_saving_mode("high")

    # def test_set_source(self):
    #    self.tv.set_sources('cec', port=3)

    def test_system_info(self):
        print(self.tv.get_system_info())

    def test_send_ircc(self):
        self.tv.send_ircc("VolumeUp")

    # def test_all_cmds(self):
    #     print(self.tv.get_all_commands())

    def test_sources_list(self):
        for s in self.tv.get_connected_sources():
            print(s)

    # def test_zz_off(self):
    #     self.tv.off()
    #     sleep(0.5)
    #     self.assertFalse(self.tv.power)


class KDL48W585BTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tv = KDL48W585B("192.168.10.5", mac="FC:F1:52:2A:9B:1E")
        cls.tv.watcher.add_report_handler(print)

    def test_volume(self):
        self.tv.volume_up()
        sleep(0.5)
        self.tv.volume_down()

    def test_channels(self):
        self.tv.channel_up()
        sleep(1)
        self.tv.channel_down()
        sleep(1)
        self.tv.set_channel(101)

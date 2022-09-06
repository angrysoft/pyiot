from time import sleep
import unittest
import os
from pyiot.xiaomi import GatewayInterface

# sid = '0x000000000545b741'
ctrlNeural1 = "158d00024e2e5b"
ctrlNeural2 = "158d00029b1929"


class TestGateway(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        passwd = os.environ.get("GWPASSWD")
        cls.gw = GatewayInterface(gwpasswd=passwd)
        cls.gw.watcher.add_report_handler(print)

    def test_token(self):
        self.assertIsInstance(self.gw.get_key(), str)

    def test_get_device_list(self):
        ret = self.gw.get_devices_list()
        print(ret)

    def test_get_id_list(self):
        ret = self.gw.get_id_list()
        print(ret)
        self.assertIsInstance(ret, list)

    def test_set_acces(self):
        ret = self.gw.accept_join()
        print(ret)

#!/usr/bin/python

from pyiot.sonoff.zigbee import SNZB01, SNZB03
from time import sleep
import unittest
from pyiot.zigbee.zigbee2mqtt import Zigbee2mqttGateway

sid = "0x00124b0022ec93cf"
sid2 = "0x00124b001f4502db"


class TestSonoffZigbee(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agw = Zigbee2mqttGateway(
            host="192.168.10.4", user="homedaemon", password="spyb0tk34s"
        )
        cls.agw.watcher.add_report_handler(print)
        cls.dev = SNZB03(sid, cls.agw)
        # cls.dev.watcher.add_report_handler(print)
        cls.dev2 = SNZB01(sid2, cls.agw)
        # cls.dev2.watcher.add_report_handler(print)

    def test_motion(self):
        sleep(240)

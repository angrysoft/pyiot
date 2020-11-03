import unittest
from pyiot.status import DeviceStatus, Attribute

class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.status = DeviceStatus()
    
    def test_a_sid(self):
        sid_attr = Attribute('sid', str, value="123345678900")
        self.status.register_attribute(sid_attr)
        self.assertEqual(self.status.sid, "123345678900")
    
    def test_a_readonly(self):
        ro_attr = Attribute('test', str, readonly=True)
        self.status.register_attribute(ro_attr)
        with self.assertRaises(AttributeError):
            self.status.test = 'foo'
    
    def test_a_readonly_oneshot(self):
        ro_attr = Attribute('test_oneshot', str, readonly=True, oneshot=True)
        self.status.register_attribute(ro_attr)
        
        self.status.test_oneshot = 'foo'
        self.assertEqual(self.status.test_oneshot , 'foo')
           
        with self.assertRaises(AttributeError):
            self.status.test_oneshot = 'bar'
            
            
        
        
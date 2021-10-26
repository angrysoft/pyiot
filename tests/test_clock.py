import unittest
from pyiot.software import Time


class TestTime(unittest.TestCase):

    def test_eq(self):
        one = Time(23, 0)
        two = Time(23, 0)
        self.assertEqual(one, two)
    
    def test_ne(self):
        one = Time(23, 0)
        two = Time(22, 0)
        self.assertNotEqual(one, two)
    
    def test_lt(self):
        one = Time(22, 0)
        two = Time(23, 0)
        self.assertLess(one, two)
    
    def test_le(self):
        one = Time(22, 0)
        two = Time(23, 0)
        self.assertLessEqual(one, two)
    
    def test_gt(self):
        one = Time(23, 0)
        two = Time(20, 0)
        self.assertGreater(Time(23, 0), Time(20, 0))
    
    def test_ge(self):
        one = Time(23, 0)
        two = Time(20, 0)
        self.assertGreaterEqual(one, two)
        three  = Time(11)
        four = Time(11)
        self.assertGreaterEqual(three, four)
    
    def test_repr(self):
        one = Time(23,22)
        print(type(one), one)
        self.assertEqual(one.__repr__(), "23:22:00")
    
    def test_get_time_now(self):
        self.assertIsInstance(Time.get_time_now(), Time)

import unittest

from monitor_trade import convert


class TestMonitorTrade(unittest.TestCase):

    def test_convert_float(self):
        self.assertEquals(convert('0.02'), 0.02)

    def test_convert_satoshi(self):
        self.assertEquals(convert('13200s'), 0.00013200)

    def test_convert_hundred_satoshi(self):
        self.assertEquals(convert('146.61S'), 0.00014661)


if __name__ == "__main__":
    unittest.main()

# test_monitor_trade.py ends here

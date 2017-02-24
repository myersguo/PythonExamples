# -*- coding: utf-8 -*-
# author: myersguo
#

import unittest
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../")
from adb.utility import adb_helper

# from utility import adb_helper

def run():
    suit = unittest.TestLoader().loadTestsFromTestCase(AdbTest)
    unittest.TextTestRunner(verbosity=2).run(suit)


class AdbTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.adb = adb_helper.AdbHelper()

    def setUp(self):
        '''
        测试用例执行之前执行
        :return:
        '''
        #self.adb = adb_helper.AdbHelper()
        pass

    def tearDown(self):
        pass

    # test execshell
    def test_execshell(self):
        devices = self.adb.execshell("devices")
        devices2 = self.adb.getConnectDevices()

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_windows_support(self):
        self.assertTrue(adb_helper.is_windows(),'This is Windows')


    def test_reconnect(self):
        self.adb.reconnect()

    def test_ps(self):
        self.adb.checkProcess("a")

    def test_push_pull(self):
        self.adb.push("D:\\a.txt", "/sdcard/a.txt")
        self.adb.pull( "/sdcard/a.txt", "D:\\b.txt")
        self.assertTrue(os.path.exists("D:/b.txt"))


if __name__ == "__main__":
    #unittest.main()
    run()
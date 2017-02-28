# -*- coding: utf-8 -*- #
# author: myersguo

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../")
from adb.utility import adb_helper

class Monkey(object):
    def __init__(self):
        self.adb = adb_helper.AdbHelper()

    def run(self, args):
        '''
        执行monkey命令，
        :param args:
        :return:
        '''
        devices = self.adb.getConnectDevices()
        for device in devices:
           self.adb.logger.debug("Device Id: %s Run monkey script:")
           self.adb.setDeviceId(device['uuid'])
           self.adb.shell("monkey " + args, wait=False)

if __name__ == "__main__":
    monkeytool = Monkey()
    monkey_argv = sys.argv
    if len(monkey_argv)>1:
        arg = monkey_argv[1]
    else:
        arg = '-v -v -v --pct-syskeys 0 --pct-motion 0 --throttle 300 --bugreport 100000'
    monkeytool.run(arg)

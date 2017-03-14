# -*- coding: utf-8 -*- #
# author: myersguo

import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../")
reload(sys)
sys.setdefaultencoding('utf-8')

from adb.utility import adb_helper
from jinja2 import Template
import time,datetime

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
        if len(devices)<=0:
            raise Exception("No device found")

        for device in devices:
           self.adb.logger.debug("Device Id: %s Run monkey script:" % device['uuid'])
           self.adb.setDeviceId(device['uuid'])
           result,_ = self.adb.shell("monkey " + args, wait=False)
           print("start monkey %s "  % result)
        #获取统计数据
        cpu_data = []
        mem_data = []
        time.sleep(3)
        while(True):
            #检查monkey是否结束
            pid = self.adb.getPIDByName('com.android.commands.monkey')
            if len(pid)<=0:
                print "no monkey start now.stop."
                break
            result1, cpu = self.adb.getCpuUsage()
            result2, mem = self.adb.getMemFree()
            if not result1 or not result2:
                continue
            mem = float(mem.split()[0])
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            cpu_data.append([t,cpu])
            mem_data.append([t,mem])
        #输出为html report
        template_file = os.path.dirname(os.path.abspath(__file__))+"/../template/performance.html"
        f = open(template_file)
        template_str = f.read()
        template = Template(template_str)
        out = template.render({"cpuinfo": cpu_data, "meminfo": mem_data})
        dest_file = os.path.dirname(os.path.abspath(__file__))+"/../output/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime()) + "_monkey_performance.html"
        f = open(dest_file, 'w')
        f.write(out)
        generateHtml()

def generateHtml():
    '''
    获取所有output，生成index.html
    '''
    output_path = os.path.dirname(os.path.abspath(__file__))+"/../output/";
    files = [f for f in os.listdir(output_path) if f != 'index.html' and os.path.isfile(os.path.join(output_path, f))]
    template_file = os.path.dirname(os.path.abspath(__file__)) + "/../template/index.html"
    f = open(template_file)
    template_str = f.read()
    template = Template(template_str)
    out = template.render({"files": files})
    dest_file = os.path.dirname(os.path.abspath(__file__)) + "/../output/index.html"
    f = open(dest_file, 'w')
    f.write(out)

if __name__ == "__main__":
    monkeytool = Monkey()
    monkey_argv = sys.argv
    if len(monkey_argv)>1:
        arg = ' '.join(monkey_argv[1:])
    else:
        arg = '-v -v -v -p com.example.android.testing.uiautomator.BasicSample --pct-syskeys 0 --pct-motion 0 --throttle 300 --bugreport 100'
    monkeytool.run(arg)

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
        self.adb.killAdbServer()
        self.adb.startAdbServer()

    def run(self, args):
        '''
        执行monkey命令，
        :param args:
        :return:
        '''
        devices = self.adb.getConnectDevices()
        if len(devices)<=0:
            raise Exception("No device found")
        process = None
        arg_list = args.split(' ')
        package_name = None
        if '-p' in arg_list:
            package_name = arg_list[arg_list.index('-p')+1]
        #monkey日志保存到文件中
        for device in devices:
           self.adb.logger.debug("Device Id: %s Run monkey script:" % device['uuid'])
           self.adb.setDeviceId(device['uuid'])
           monkey_log = os.path.dirname(os.path.abspath(__file__))+"/../output/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime()) + "_monkey_log.txt"
           f = open(monkey_log, 'a')
           result,process = self.adb.shell("monkey " + args, wait=False, stdout=f)
        #获取统计数据
        cpu_data = []
        mem_data = []
        cpu_pkg_data = []
        mem_pkg_data = []
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
            #t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            t = float(round(time.time() * 1000))
            cpu  = float("%.2f" % cpu)
            mem = float("%.2f" % mem)
            cpu_data.append([t,cpu])
            mem_data.append([t,mem])
            if  package_name:
                result3, p_cpu = self.adb.getProcessCpuUsage(package_name)
                if result3:
                    p_cpu = float("%.2f" % p_cpu)
                    cpu_pkg_data.append([t,p_cpu])
                result4, p_mem = self.adb.getDumpmeminfo(package_name)
                if result4:
                    p_mem = float(p_mem.split()[1])
                    mem_pkg_data.append([t, p_mem])


        #输出为html report
        template_file = os.path.dirname(os.path.abspath(__file__))+"/../template/performance.html"
        f = open(template_file)
        template_str = f.read()
        template = Template(template_str)
        out = template.render({"cpuinfo": cpu_data, "meminfo": mem_data, "pcpu": cpu_pkg_data,"pmem": mem_pkg_data, "package_name": package_name})
        dest_file = os.path.dirname(os.path.abspath(__file__))+"/../output/" + time.strftime("%Y-%m-%d_%H_%M_%S", time.gmtime()) + "_monkey_performance.html"
        f = open(dest_file, 'w')
        f.write(out)
        generateHtml()

def generateHtml():
    '''
    获取所有output，生成index.html
    '''
    output_path = os.path.dirname(os.path.abspath(__file__))+"/../output/";
    files = [f for f in os.listdir(output_path) if  f.endswith('.html') and   f != 'index.html' and os.path.isfile(os.path.join(output_path, f))]
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

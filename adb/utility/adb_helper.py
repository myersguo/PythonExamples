#-*- coding: utf-8 -*-
"""
adb help tools
get device list
get api level
get platform version

execute monkey script
start app
"""
import os
import logging
import subprocess
import re
import time

def is_windows():
    if os.name in ('nt','ce'):
        return True
    return False

#---------------------------------------------------------------------------
# 模块工具类方法
# 获取Adb对象
#---------------------------------------------------------------------------
def getAdb(name):
    pass

class AdbHelper (object):
    """
    ADB 命令行方法帮助类
    """
    def __init__(self, opts={}):
        """
        初始化方法，opts为一个map类型参数
        """
        if 'sdkRoot' in opts:
            self.sdkRoot = opts.sdkRoot
        elif "ANDROID_HOME" in os.environ:
            self.sdkRoot = os.environ['ANDROID_HOME']
        self.iswindows = is_windows()
        result,self.adb = self._checkaSdkBinarypresent('adb')
        if not result:
            raise Exception("adb tool not found")
        if 'logfile' in opts:
            self.logfile = opts.logfile
        else:
            self.logfile = os.getcwd() + os.sep + "adb.log"
        if 'log_level' in opts:
            self.log_level = opts.log_level
        else:
            self.log_level = logging.DEBUG

        self.logger = logging.getLogger("adb_log")
        self.logger.setLevel(self.log_level)
        #log to file
        log_fileHandler = logging.FileHandler(self.logfile)
        log_formater = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        log_fileHandler.setFormatter(log_formater)
        self.logger.addHandler(log_fileHandler)
        #default argument of adb
        self.adb_defaultArgs = []
        self.devices = []
        self.binarySearchPath = []

    def _checkaSdkBinarypresent(self, binary):
        '''
        检查android工具,
        platform-tools: 平台工具,adb,dmtracedump
        tools: ddms,android,monitor,monkeyrunner,traceview,uiautomatorviewer
        build-tools: android各平台的构建工具,appt,aapt2,zipalign,
        :param binary:
        :return:
        '''
        binaryName = binary
        if self.iswindows:
            if not binaryName.endswith(".exe"):
                binaryName = binaryName + ".exe"
        if not self.sdkRoot:
            raise   Exception("%s not found", binaryName)
        self.binarySearchPath = []
        platform_tools_binary =  self.sdkRoot + os.sep + "platform-tools" + os.sep + binaryName
        tools_binary = self.sdkRoot + os.sep + "tools" + os.sep + binaryName
        build_tools_path = self.sdkRoot + os.sep + "build-tools"
        build_tools_binarys = [build_tools_path + os.sep + build_tools_dir + os.sep + binaryName for build_tools_dir in os.listdir(build_tools_path)]
        self.binarySearchPath.append(platform_tools_binary)
        self.binarySearchPath.append(tools_binary)
        self.binarySearchPath += build_tools_binarys
        for bi in self.binarySearchPath:
            if os.path.exists(bi):
                return True,bi

        raise   Exception("%s not found", binaryName)
    def shell(self, cmd, wait=True):
        return self.execshell("shell %s" % cmd, wait)

    def execshell(self,cmd, wait=True):
        if not cmd:
            raise Exception("command can't be empty")
        fullCmd = self.adb + " " +  " ".join(self.adb_defaultArgs) + " " + cmd
        #return os.popen(fullCmd).readline()
        try:
            process = subprocess.Popen(fullCmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (OSError, ValueError) as err:
            self.logger.error("Run %s command Exception", fullCmd)
            raise Exception("subprocesserror")
        if wait == False:
            return True,''
        stdoutdata, stderrdata = process.communicate()
        self.logger.debug(fullCmd + " status " + str(process.returncode))
        if process.returncode:
            return False, stderrdata
        else:
            return True,stdoutdata
        # result = []
        # while True:
        #     output = process.stdout.readline()
        #     if output != '':
        #         result.append(output)
        #     else:
        #         break
        # return  result

    def setDeviceId(self, deviceId):
        self.currentDeviceId = deviceId
        if not "-s " + deviceId in self.adb_defaultArgs:
            self.adb_defaultArgs.append("-s " + deviceId)

    def getConnectDevices(self):
        self.logger.debug("Get connected devices")
        result,output_lines = self.execshell("devices")
        _devices = []
        for line in output_lines.split('\r\n'):
            if line.strip() and line.find("List of devices") == -1 and line.find("* daemon") == -1 and line.find("offline")==-1:
                lineinfo = line.split("\t")
                _devices.append({"uuid":lineinfo[0], "state": lineinfo[1]})
        self.devices = _devices
        self.logger.debug(str(len(self.devices)) + " device(s) connected")
        return self.devices
    def reconnect(self):
        self.logger.debug("Reconnect devices")
        self.execshell("reconnect")

    def killAdbServer(self):
        """
        kill adb server by shell
        """
        return self.execshell("kill-server")

    def checkProcess(self, processName):
        '''
        检查进程是否存在
        adb shell ps 将输出
        USER     PID   PPID  VSIZE  RSS     WCHAN    PC         NAME
        :param processName:
        :return:
        '''
        self.logger.debug("Check process %s" % processName)
        result,output = self.execshell("shell ps")
        for line in output.split("\r\n"):
            line = line.strip().split()
            if not line:
                continue
            _t = line[len(line)-1]
            if _t and _t.find(processName) !=-1:
                self.logger.debug("Find process %s from %s" % (processName, _t) )
                return True

        self.logger.debug("Canot find process %s" % processName)
        return False

    def push(self, localPath, remotePah):
        return self.execshell("push %s %s  " % (localPath,remotePah) )

    def pull(self, remotePath, localPath):
        return self.execshell("pull %s %s\r\n" % (remotePath, localPath) )

    def forwardPort(self, systemPort, devicePort):
        '''
        adb forward <local> <remote> - forward socket connections
                                 forward specs are one of:
                                   tcp:<port>
                                   localabstract:<unix domain socket name>
                                   localreserved:<unix domain socket name>
                                   localfilesystem:<unix domain socket name>
                                   dev:<character device name>
                                   jdwp:<process pid> (remote only)
        :param systemPort:  PC机的端口号
        :param devicePort:  设备(手机、模拟器)端口号
        :return:
        '''
        return self.execshell("forward tcp: %s tcp: %s" % (systemPort, devicePort))

    def isDeviceConnected(self):
        devices = self.getConnectDevices()
        if len(devices) > 0:
            return True
        else:
            return False

    def getPIDByName(self, name):
        command = " shell ps '%s'" % name
        result, output = self.execshell(command)
        pids = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            m = re.match("[^\t ]+[\t ]+([0-9]+)", line)
            if m is not None:
                pids.append(m.group(1))
        return pids

    def killProcessByPID(self, pid):
        '''
        需要root权限
        :param pid:
        :return:
        '''
        return self.shell("kill  %s" % pid)

    def killProcessByName(self, name):
        pids = self.getPIDByName(name)
        for pid in pids:
            self.logger.debug('kill process %s' % pid)
            self.killProcessByPID(pid)

    def uiautomator_dump(self, path):
        self.shell("uiautomator dump /sdcard/window_dump.xml")
        return self.pull("/sdcard/window_dump.xml", path)

    def clear(self, pkg):
        return self.shell("pm clear %s " % pkg)

    def forceStop(self, pkg):
        return self.shell("am force-stop %s " % (pkg,))

    def install(self, apk, replace=True):
        cmd = 'install'
        if replace:
            cmd +=  ' -r '
        cmd += '"%s"' % apk
        return self.execshell(cmd)

    def uninstall(self, pkg):
        self.forceStop(pkg)
        result = self.execshell("uninstall %s " % (pkg,))
        if result.find("Success") == -1:
            self.logger.debug("App was not uninstalled")
        else:
            self.logger.debug("App was uninstalled")

    def mkdir(self, path):
        return self.shell('mkdir -p %s' % (path))
    def remove(self, path):
        return self.shell("rm -rf %s" % (path))

    def screenshot(self, despath):
        '''
        截屏
        :param despath:
        :return:
        '''
        path = '/sdcard/%s.png' % (time.time(),)
        self.shell("screencap -p %s" % (path,))
        self.pull(path, despath)
        self.remove(path)

    def exescript(self, path):
        '''
        执行本地脚本
        push script file to /data/local/tmp/
        增加执行权限
        chmod 0777 /data/local/tmp/file
        执行脚本
        /data/local/tmp/file
        :param path:
        :return:
        '''
        destFile = "/data/local/tmp/" + str(time.time()) + ".sh"
        result,_ = self.push(path,destFile)
        if not result:
            return False,'push file (%s) to device failed' % path
        cmd = "chmod 0777 %s" % destFile
        result,_ = self.shell(cmd)
        if not result:
            return False, 'change file (%s) mod failed' % destFile
        self.logger.debug("exec script: %s" % destFile)
        return self.shell(destFile, False)



#!/usr/bin/python3

import modules.check.CommonCheck as common


class ProxyServerCheck(common.CommonCheck):

    def __init__(self, config, logger):
        super().__init__(config, logger)

    def check(self):

        dc = self.configData['local']['dc_check']
        my_dc = self.configData['local']['whoami']
        hostToPing = self.configData[dc]['proxy_ip']
        checkDownFile_preconfigure = self.configData['local']['checkDownFile']
        checkDownFile = checkDownFile_preconfigure + '-{}'.format(self.configData['local']['role'])
        checkPromotionFile_preconfigure = self.configData['local']['checkPromotionFile']
        checkPromotionFile = checkPromotionFile_preconfigure + '-{}'.format(self.configData['local']['role'])
        provider = self.configData['local']['provider']
        proxy_switch = self.configData['local']['proxy_switch']
        activate_cmds = self.configData[my_dc]['proxy_switch'][proxy_switch]['activate']
        deactivate_cmds = self.configData[my_dc]['proxy_switch'][proxy_switch]['deativate']
        enable_activate = self.configData['local']['proxy_enable_activate']
        enable_deactivate = self.configData['local']['proxy_enable_deactivate']
        if proxy_switch != "bgp":
            self.logger_session.error("only supported proxy switch is bgp")

        if self.pingHost(hostToPing):
            self.logger_session.info("Host is reachable")
            downStatus = self.lockFileExists(checkDownFile)
            promoteStatus = self.lockFileExists(checkPromotionFile)

            if downStatus and promoteStatus:
                self.logger_session.info("DC1 online deactivate bgp")
                for deactivate_cmd in deactivate_cmds:
                    self.logger_session.info("Command:{}".format(deactivate_cmd))
                    if enable_deactivate:
                        self.runCmdRawOutput(deactivate_cmd)
            if self.lockFileExists(checkDownFile):
                self.removeFile(checkDownFile)
            if self.lockFileExists(checkPromotionFile):
                self.removeFile(checkPromotionFile)
        else:
            if self.statusCheckVM(self.configData[dc]['proxyserver_vmname'], provider, self.configData):
                self.logger_session.info("Host not reachable but VM is running")
            else:
                if self.lockFileExists(checkPromotionFile):
                    self.logger_session.info("VM is down and bgp switch in process ")
                else:
                    self.logger_session.info("proxy VM is down")
                    self.logger_session.info("Run bgp switch")
                    for activate_cmd in activate_cmds:
                        self.logger_session.info(
                            "Command: {}".format(activate_cmd))
                        if enable_activate:
                            self.runCmdRawOutput(activate_cmd)
                    self.createFile(checkDownFile, "")
                    self.createFile(checkPromotionFile, "")

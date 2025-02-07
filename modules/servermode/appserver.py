#!/usr/bin/python3

import modules.check.CommonCheck as common


class AppServerCheck(common.CommonCheck):

    def __init__(self, config, logger):
        super().__init__(config, logger)

    def check(self):

        dc = self.configData['local']['dc_check']
        hostToPing = self.configData[dc]['appserver_ip']
        sourceMailHost = self.configData[dc]['appserver_vmname']
        checkDownFile_preconfigure = self.configData['local']['checkDownFile']
        checkDownFile = checkDownFile_preconfigure + '-{}'.format(self.configData['local']['role'])
        checkPromotionFile_preconfigure = self.configData['local']['checkPromotionFile']
        checkPromotionFile = checkPromotionFile_preconfigure + '-{}'.format(self.configData['local']['role'])
        checkStopHaModule = self.configData['local']['checkRestartReplicaFile']
        provider = self.configData['local']['provider']
        threads = self.configData['local']['threads']
        disable_ha_module = self.configData['local']['disable_ha_module']
        flush_cache = self.configData['local']['flush_cache']
        flush_arguments_a = self.configData['local']['flush_arguments_a']
        restart_replica = self.configData['local']['restart_replica']

        if self.pingHost(hostToPing):
            self.logger_session.info("Host is reachable")
            if self.lockFileExists(checkDownFile):
                self.removeFile(checkDownFile)
            if self.lockFileExists(checkPromotionFile):
                self.removeFile(checkPromotionFile)
            if self.lockFileExists(checkStopHaModule):
                if disable_ha_module:
                    self.logger_session.info("Start HA module Carbonio")
                    self.runCmdRawOutput("su - zextras -c 'carbonio ha doStartService module'")
                    self.removeFile(checkStopHaModule)
        else:
            # if vcenter show VM status running
            if self.statusCheckVM(self.configData[dc]['appserver_vmname'], provider, self.configData):
                self.logger_session.info("Host not reachable but VM is running")
                if self.lockFileExists(checkPromotionFile):
                    self.removeFile(checkPromotionFile)
            # if vcenter show VM status stopped
            else:
                if self.lockFileExists(checkPromotionFile):
                    self.logger_session.info("app VM is down and promotion in process ")
                    output = self.runCmdJsonOutput("su - zextras -c 'carbonio --json core getAllOperations'")
                    # if no carbonio process(replace with processID)
                    # if len(output["response"]["operationList"]) == 0:
                    #     self.logger_session.info("Promotion not in process.")
                    #     self.removeFile(checkPromotionFile)
                elif self.configData['local']['whoami'] == "primary":
                    self.logger_session.info(self.configData['local']['whoami'])
                    self.logger_session.info("Promotion on primary dc should be done manually")
                    if not self.lockFileExists(checkStopHaModule):
                        if disable_ha_module:
                            self.logger_session.info("Stop HA module Carbonio")
                            self.runCmdRawOutput("su - zextras -c 'carbonio ha doStopService module'")
                            self.createFile(checkStopHaModule, "")
                else:
                    self.logger_session.info("app VM is down")
                    output = self.runCmdJsonOutput("su - zextras -c '/opt/zextras/bin/carbonio --json  ha  getAccountStatus "
                                          "mailHost {source_mail_host}'".format(source_mail_host=sourceMailHost))
                    if "response" in output:
                        accounts = output["response"]["values"]
                        if len(accounts) != 0:
                            self.logger_session.info("Run promoteAccounts")
                            output = self.runCmdRawOutput(
                                "su - zextras -c '/opt/zextras/bin/carbonio --sync ha promoteAccounts source_mail_host "
                                "{source_mail_host} threads {threads}'".format(threads=threads,
                                                                               source_mail_host=sourceMailHost))
                            self.createFile(checkDownFile, "")
                            self.createFile(checkPromotionFile, "")
                            if flush_cache:
                                argument = ""
                                if flush_arguments_a:
                                    argument = "-a"
                                self.logger_session.info("Flush the cache for promoted accounts")
                                for account in accounts:
                                    self.runCmdRawOutput("su - zextras -c '/opt/zextras/bin/zmprov fc {argument} "
                                                         "account {account}'"
                                                         .format(account=account["accountName"], argument=argument))
                            if restart_replica:
                                for account in accounts:
                                    self.logger_session.info("Restart replication")
                                    self.runCmdJsonOutput("su - zextras -c 'carbonio --json  ha pauseReplicas accounts "
                                                          "{account}'".format(account=account["accountName"]))
                                    self.runCmdJsonOutput("su - zextras -c 'carbonio --json  ha restartReplicas accounts "
                                                          "{account}'".format(account=account["accountName"]))
                        else:
                            self.logger_session.info("Accounts not present on {source_mail_host}".format(source_mail_host=sourceMailHost))
                    else:
                        self.logger_session.info("Promotiona were blocked ")
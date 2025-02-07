#!/usr/bin/python3

import os
import time
import modules.check.CommonCheck as common
import modules.provider.consul as consul
import json


class ConsulServerCheck(common.CommonCheck):

    def __init__(self, config, logger):
        super().__init__(config, logger)

    def check(self):
        dc = self.configData['local']['dc_check']
        hostsToPing = self.configData[dc]['consul_ips']
        hostsToCheck = self.configData[dc]['consul_vmnames']
        checkDownFile_preconfigure = self.configData['local']['checkDownFile']
        checkDownFile = checkDownFile_preconfigure + '-{}'.format(self.configData['local']['role'])
        checkPromotionFile_preconfigure = self.configData['local']['checkPromotionFile']
        checkPromotionFile = checkPromotionFile_preconfigure + '-{}'.format(self.configData['local']['role'])
        provider = self.configData['local']['provider']
        #waitTime = self.configData['local']['waitfor']

        pingList = [self.pingHost(host) for host in hostsToPing]
        print(pingList)
        if True in pingList:
            if self.lockFileExists(checkDownFile):
                self.removeFile(checkDownFile)
            if self.lockFileExists(checkPromotionFile):
                self.removeFile(checkPromotionFile)
        else:
            vmcheckList = [self.statusCheckVM(hostname, provider, self.configData) for hostname in hostsToCheck]
            if True in vmcheckList:
                self.logger_session.info("Host not reachable but VM is running")
                if self.lockFileExists(checkPromotionFile):
                    self.removeFile(checkPromotionFile)
            # if vcenter show VM status stopped
            else:
                if self.lockFileExists(checkDownFile):
                    self.logger_session.warning("Consul recovery already started")
                else:
                    self.logger_session.warning("Consul server must be elected manually")
                    self.manageService("service-discover", "stop")
                    os.popen('cp /etc/hamon/peers.json /var/lib/service-discover/data/raft/peers.json')
                    self.manageService("service-discover", "start")
                    time.sleep(3)
                    os.popen('cp /etc/hamon/peers.json /var/lib/service-discover/data/raft/peers.json')
                    self.manageService("service-discover", "restart")
                    self.createFile(checkPromotionFile, "")
                    self.createFile(checkDownFile, "")

    def create_peers(self):
        ip = self.get_my_ip
        c = consul.Consul("localhost", "8300")
        peers = c.create_peers_file()
        peers_json = json.dumps(peers, indent=4)
        with open("peers.json", "w") as outfile:
            outfile.write(peers_json)

    def create_recovery_peers(self, remove_ip):
        with open("peers.json", "r") as outfile:
            peers = json.load(outfile)
        new_peers = list()
        for peer in peers:
            tmp = peer["address"].split(":")[0]
            if tmp != remove_ip:
                new_peers.append(peer)
        peers_recovery_json = json.dumps(new_peers, indent=4)
        with open("peers_recovery.json", "w") as outfile:
            outfile.write(peers_recovery_json)
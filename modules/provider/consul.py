import requests
import urllib3
from modules.provider.CommonProvider import CommonProvider
import consul


class CONSUL(CommonProvider):

    def __init__(self, config, logfile):
        super().__init__(config, logfile)

    def check(self, hostname):
        consulhost = self.config["consul"]["hostname"]
        port = self.config["consul"]["port"]
        token = self.config["consul"]["token"]
        c = consul.Consul(consulhost, port)

        members = c.agent.members()
        hostname = hostname.replace(".", "-")
        status = False
        node_status = 1 # 1 - healthy 3 - not healthy
        for member in members:
            member_name = member["Name"]
            member_name = member_name.replace("agent-", "")
            member_name = member_name.replace("server-", "")
            if member_name == hostname:
                node_status = member["Status"]
                if not node_status == 1:
                    status = False
                else:
                    status = True
                break

        return status

class Consul:

    def __init__(self, host: str, port: str):
        self.consulPort = port
        self.consulHost = host
        self.allServices = list()

    def getAllServices(self):
        c = consul.Consul(host=self.consulHost, port=self.consulPort)
        allServicesInfo = c.catalog.services()
        services = list()
        for name, value in allServicesInfo[1].items():
            services.append(name)
        self.allServices = services

    def checkAllServices(self) -> str:
        print("start check consul services")
        reportList = list()
        self.getAllServices()
        for service in self.allServices:
            reportLine = self.checkService(service)
            reportList.append(reportLine)
        print("stop check consul services")
        reportStr = '\n'.join(reportList)
        return reportStr

    def checkService(self, serviceName: str) -> str:
        c = consul.Consul(host=self.consulHost, port=self.consulPort)
        serviceInfo = c.health.service(service=serviceName)

        # print(type(serviceInfo[1][0]["Checks"]))
        try:
            # print(serviceInfo[1][0]["Checks"][1])
            serviceID = serviceInfo[1][0]["Checks"][1]["CheckID"]
            healthStatus = serviceInfo[1][0]["Checks"][1]["Status"]
            reportLine = f"{serviceID}\t\t\tstatus: {healthStatus}"
        except IndexError:
            reportLine = f"service:{serviceName} status: have only agent check"

        return reportLine

    def create_peers_file(self):
        c = consul.Consul(host=self.consulHost, port=self.consulPort)
        members = c.agent.members()
        peers = list()
        for member in members:
            peer = ""
            if member["Tags"]["role"] == "consul" and member["Status"] == 1:
                peer = {"id": member["Tags"]["id"], "address": "{}:{}".format(member["Addr"], member["Port"]),
                        "non_voter": "false"}
                peers.append(peer)
        return peers

    def cluster_leader(self):
        c = consul.Consul(host=self.consulHost, port=self.consulPort)
        leader = c.status.leader()
        return leader

    def node_check(self):
        pass

import requests
import json
from modules.provider.CommonProvider import CommonProvider

class HETRIX(CommonProvider):

    def __init__(self, config, logfile):
        super().__init__(config, logfile)

    def check(self, hostname):
        apikey = self.config["hetrix"]["api_token"]
        host = self.config["hetrix"]["hostname"]

        session = requests.get("https://{host}/v1/{apikey}/status/".format(apikey=apikey, host=host))
        status = session.status_code
        if status == 200:
            print(session.json())

        # get VM id
        session = requests.get(
            "https://{host}/v1/{apikey}/uptime/monitors/{page_num}/{num_on_page}/".format(
                apikey=apikey, page_num=0, num_on_page=30, host=host)
        )
        status = session.status_code
        vm_id = ""
        if status == 200:
            try:
                VMs = session.json()[0]
                for VM in VMs:
                    if VM["Name"] == hostname:
                        vm_id = VM["ID"]
                        self.logger.info(VM["ID"])
            except KeyError:
                self.logger.info(session.json())
                self.logger.error("We can't define VM is running or not")
                return True # We can define VM is running or not

        statusVM = False
        session = requests.get(
            "https://{host}/v1/{apikey}/uptime/report/{vm}/".format(apikey=apikey, vm=vm_id, host=host))
        status = session.status_code
        if status == 200:
            try:
                self.logger.info(session.json()["Uptime_Stats"]["Total"]["Uptime"])
                self.logger.info(session.json()["Uptime_Status"])
                if session.json()["Uptime_Status"] == "Online":
                    statusVM = True
                    self.logger.info("VM is POWERED_ON {vmname}".format(vmname=hostname))
            except KeyError:
                self.logger.error("Unnable to find host: {hostname} in hetrix".format(hostname=hostname))
                self.logger.error("We can't define VM is running or not")
                statusVM = True # We can define VM is running or not
        return statusVM

    def checkv3(self, hostname):
        apikey = self.config["hetrix"]["api_token"]
        host = self.config["hetrix"]["hostname"]
        headers = {"Authorization": "Bearer {token}".format(token=apikey)}
        session = requests.get("https://api.hetrixtools.com/v3/status-pages".format(apikey=apikey, host=host),
                               headers=headers)
        status = session.status_code
        if status == 200:
            print(session.json())

        # get VM id
        session = requests.get(
            "https://api.hetrixtools.com/v3/uptime-monitors".format(
                apikey=apikey, page_num=0, num_on_page=30, host=host), headers=headers
        )
        status = session.status_code
        vm_id = ""
        statusVM = False
        statusVM_report = "down"
        if status == 200:
            try:
                VMs = json.loads(session.content.decode('utf-8'))
                for VM in VMs["monitors"]:
                    if VM["name"] == hostname:
                        statusVM_report = VM["uptime_status"]
                        self.logger.info(VM["uptime_status"])
            except KeyError:
                self.logger.info(session.json())
                self.logger.error("We can't define VM is running or not")
                return True # We can define VM is running or not

        if statusVM_report == "up":
            statusVM = True
            self.logger.info("VM is POWERED_ON {vmname}".format(vmname=hostname))
        return statusVM

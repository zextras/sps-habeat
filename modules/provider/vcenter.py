import requests
import urllib3
from modules.provider.CommonProvider import CommonProvider


class VCENTER(CommonProvider):

    def __init__(self, config, logfile):
        super().__init__(config, logfile)

    def check(self, hostname):
        username = self.config["vcenter"]["username"]
        password = self.config["vcenter"]["password"]
        host = self.config["vcenter"]["hostname"]
        urllib3.disable_warnings()
        try:
            sess = requests.post("https://{host}/rest/com/vmware/cis/session".format(host=host),
                                 auth=('{username}'.format(username=username), '{password}'.format(password=password)),
                                 verify=False)
            session_id = sess.json()['value']
        except requests.exceptions.ConnectionError:
            self.logger.error("Vcenter is unreachable")
            return True # we can't define if VM is down

        resp = requests.get("https://{host}/rest/vcenter/vm".format(host=host), verify=False, headers={
            "vmware-api-session-id": session_id
        })
        VMlist = resp.json()["value"]
        status = True
        for VM in VMlist:
            if VM["name"] == hostname:
                self.logger.info("Check VM {vmname}".format(vmname=VM["name"]))
                if VM["power_state"] == "POWERED_OFF":
                    status = False
                    self.logger.info("VM is POWERED_OFF {vmname}".format(vmname=VM["name"]))
                    break
        return status

import os
import subprocess
import json
import platform
import modules.provider.vcenter as vcenter
import modules.provider.hetrix as hetrix
import modules.provider.consul as consul
import yaml
import socket


class CommonCheck:

    def __init__(self, config, logger):
        self.logger_session = logger
        with open(config, "r") as c:
            configData = yaml.load(c, Loader=yaml.FullLoader)
        self.configData = configData

    def statusCheckVM(self, hostname, provider, config):
        status = False
        if provider == "hetrix":
            hetrix_check = hetrix.HETRIX(config, self.logger_session)
            status = hetrix_check.checkv3(hostname)
        elif provider == "vcenter":
            vcenter_check = vcenter.VCENTER(config, self.logger_session)
            status = vcenter_check.check(hostname)
        elif provider == "consul":
            consul_check = consul.CONSUL(config, self.logger_session)
            status = consul_check.check(hostname)
        else:
            self.logger_session.error("Chosen provider {provider} doen't supported".format(provider=provider))
        return status

    def lockFileExists(self, filename):
        if os.path.exists(filename):
            return True
        else:
            return False

    def pingHost(self, host) -> bool:
        try:
            subprocess.check_output(
                "ping -{} 1 {}".format("n" if platform.system().lower() == "windows" else "c", host), shell=True
            )
        except Exception:
            self.logger_session.info("Unable to reach host {host}".format(host=host))
            return False
        self.logger_session.info("Host is reachable {host}".format(host=host))
        return True

    def runCmdJsonOutput(self, command):
        promoteCmd = ' '.join(["TERM=xterm-256color", command])
        execPromoteCmd = os.popen(promoteCmd)
        outputStr = execPromoteCmd.read()
        self.logger_session.info(outputStr)
        outputJSON = json.loads(outputStr)
        return outputJSON

    def runCmdRawOutput(self, command):
        promoteCmd = ' '.join(["TERM=xterm-256color", command])
        execPromoteCmd = os.popen(promoteCmd)
        outputStr = execPromoteCmd.read()
        self.logger_session.info(outputStr)
        return outputStr

    def createFile(self, filename, content):
        self.logger_session.info("Create lock {filename} file".format(filename=filename))
        with open(filename, "w") as c:
            c.write(content)

    def removeFile(self, filename):
        self.logger_session.info("Delete lock {filename} file".format(filename=filename))
        os.remove(filename)

    def manageService(self, process, action):
        try:
            os.popen("systemctl " + action + " " + process)
            self.logger_session.info(process + " " + action + " successfully...")
        except OSError as ose:
            self.logger_session.error("Error while running the command", ose)
        pass

    def get_my_ip(self):
        return socket.gethostbyname(self.get_my_hostname())

    def get_my_hostname(self):
        return socket.gethostname()

    def check(self):
        pass

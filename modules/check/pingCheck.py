import subprocess
from re import findall
from subprocess import Popen, PIPE

def ping(host, ping_count):
    answer = ""
    print("start check ping")
    for ip in host:
        #response = subprocess.check_output("ping -c 1 " + ip, shell=True)
        # and then check the response...
        data = ""
        output = Popen(f"ping {ip} -c {ping_count}", shell=True, stdout=PIPE, encoding="utf-8")
        ping_test = ""
        for line in output.stdout:
            data = data + line
            ping_test = findall("ttl", data)

        if ping_test:
            answer += f"{ip} : Successful Ping\n"
        else:
            answer += f"{ip} : Failed Ping\n"

        #print(answer)
    print("stop check ping")
    return answer

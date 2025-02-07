import requests
from prometheus_client.parser import text_string_to_metric_families



def metrics():
    reportLine = ""
    metrics = requests.get('http://gk-ha-svcs1.demo.zextras.io:9100/metrics').text
    for family in text_string_to_metric_families(metrics):
        if family.name == "node_load1":
            reportLine = family.samples
    print(type(reportLine[0]))
    reportList = list()
    for sample in reportLine:
        for value in sample:
           reportList.append(value)
    print(type(reportList))
    report = "\t".join(reportList)
    #report = "\n".join(reportLine)

    return report
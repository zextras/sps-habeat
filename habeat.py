#!/usr/bin/python3

import modules.servermode.appserver as appserver
import argparse
import yaml
import logging


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config', type=str, dest='configFile', default="/etc/habeat/habeat.yml",
                        help='Path for config file')
    parser.add_argument('--log', type=str, dest='logFile', default="/var/log/habeat.log",
                        help='Path for log file')
    args = parser.parse_args()

    with open(args.configFile, "r") as c:
        configData = yaml.load(c, Loader=yaml.FullLoader)

    mode = configData['local']['role']
    logging.basicConfig(format='%(asctime)s %(name)s - %(levelname)s - %(message)s', level=logging.INFO, handlers=[
        logging.FileHandler(args.logFile),
        logging.StreamHandler()
    ])
    logging.info("-------- START Check HA habeat -----------")

    if mode == "appserver":
        checkObj = appserver.AppServerCheck(args.configFile, logging)
        checkObj.check()
    else:
        print("Mode {mode} isn't defined yet. Allowed modes: appserver".format(mode=mode))

    logging.info("-------- STOP Check HA habeat -----------")


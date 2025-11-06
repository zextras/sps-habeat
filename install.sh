#!/bin/bash

echo "Copying file to sbin"
cp habeat.py /usr/local/sbin/
cp -r modules /usr/local/sbin/
chmod +x /usr/local/sbin/habeat.py

echo "Copying and enabling units"
cp habeat.service /usr/lib/systemd/system/
cp habeat.timer /usr/lib/systemd/system/
systemctl enable habeat.service
systemctl enable habeat.timer
systemctl start habeat.timer

echo "Copying logrotate conf"
cp logrotate/habeat /etc/logrotate.d/

echo "Copying config file to default folder"
mkdir -p /etc/habeat
cp config/habeat.yml /etc/habeat/
echo "Rememeber habeat.yml parameters must match your infrastrucure"
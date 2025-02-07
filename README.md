For RHEL8

`dnf install python3.12 python3-pip -y`
`pip3 install -r requirements_r8.txt`



Copy diagram  habeat.py  modules  requirements_r8.txt to /usr/loca/sbin

`cd /usr/loca/sbin`
`chmod +x habeat.py`

`mkdir /etc/habeat`
`cp habeat.yml /etc/habeat/`

Edit habeat.yml 

then check the script works /usr/local/sbin/habeat.py then enable the service

`cp habeat.service /usr/lib/systemd/system/`
`cp habeat.timer /usr/lib/systemd/system/`
`systemctl enable habeat.service`
`systemctl enable habeat.timer`
`systemctl start habeat.timer`

copy logrotate/habeat in /etc/logrotate folder


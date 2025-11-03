This is an example of  procedure to monitor a Carbonioreplicated application server and activate
the replica when it's not reachable.

### How it works

The script is installed as units and running scheduled by systemd timer.
The script reads a config file where admins must define parameters for source and destination mailstore.
The script chek if the VM running the mailbox is reachable (ping) if it id **<u>no additional check is performed</u>**!

If the source mailstore does not answer to ping the the script checks if it the source Mailstore is listed in service mesh if not 
a lock file is created, if at ne next scheduled run the lock file is still present accounts are promoted.

It can be manually run using

`/usr/local/sbin/habeat.py --config /etc/habeat/habeat.yml`

### Installation

For RHEL8

`dnf install python3.12 python3-pip -y`
`pip3 install -r requirements_r8.txt`

For Ubuntu

`pip3 install -r requirements.txt`

Edit habeat.yml 

run install.sh

The installation script:

- Copies script in the bin folder
- Creates and enavle the units and timer for systemd
- Copies the logrotate definition to /etc/logrotate.d
- Copies the config file to /etc/habeat/


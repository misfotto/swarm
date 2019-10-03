# SWARM


[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/misfotto/swarm/issues) [![HitCount](http://hits.dwyl.com/misfotto/swarm.svg)](http://hits.dwyl.com/misfotto/swarm) 


Multi-threaded Command multiplexer for SSH wich features shell commands forwarder ( with verbose output ), connection-only mode and csv reports.

**Installation**
---

Installing required modules
```
pip3 install -r requirements.txt
```
Make the script executable ( waiting for an installer :P )
```
chmod +x swarm.py
```
...and start the script and dive into the arguments :)
```
./swarm.py --help
```

**Scope**
---

Swarm can be use mainly for two tasks: 
- __Checking the SSH connectivity of remote(s) host(s)__ 
- __Forward a shell command trought ssh to remote(s) host(s)__

### Required arguments
There are, despite of your scope, some arguments that are required.

__-i, --ips:__ _Targets IPs for the swarm to connect to. IPs can be specified in comma-separeted format within the command line or can be specified a file with an ip on evely line._

```
./swarm.py --ips 192.168.0.2,192.168.0.3
```
```
./swarm.py --ips ip_list.txt
```

__-u, --ssh-user:__ _Username used to connect to remote(s) host(s)._

__-p, --ssh-password:__ _Password used to connect to remote(s) host(s)._

### Use Case #1: Checking the SSH connectivity

To only check if a remote ssh connection can be made the swarm arguments are these

```
./swarm.py --ips 192.168.0.2,192.168.0.3 -u username -p password --connect-only --verbose
```

### Use Case #2: Checking the SSH connectivity

To forward a shell command to remote(s) host(s)

```
./swarm.py --ips 192.168.0.2,192.168.0.3 -u username -p password --cmd "uname -a" -v
```

This command will connect to remote host(s) and forwardthe command specified with the __--cmd__ parameter.

## Extra Arguments


### Multithreading ( -t, --threads )

```
./swarm.py --ips ip_list.txt --cmd "uname -a" --threads 20
```
Change the default multithread limit ( Default: 4 ) to customize the speed.

_Tip: Avoid thread > ~200 this will break the ulimit._


### Create a Report ( -o, --output )

```
./swarm.py --ips ip_list.txt --cmd "uname -a" -o report
```
Creates a report of the swarm action. The output will be a csv file named: __<name_specified>.swarm.csv__ and will have a record for every remote host the swarm connects to.


**How to Contribute**
---

1. Clone repo and create a new branch: `$ git checkout https://github.com/misfotto/swarm -b name_for_new_branch`.
2. Make changes and test
3. Submit Pull Request with comprehensive description of changes

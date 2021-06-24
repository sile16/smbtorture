# smbtorture

A tool to create many SMB Client connections and simulate a workload.  It uses asyncio rather than threads, as there are challenges creating 1000's of threads.  However, it is using the smbclient as a separate process and essentially sending commands to smbclient.  So, seperate processes are spawned for each connection.  These means we can take advantage of multiple CPUs.   It requires ~1GB of RAM per 120 connections.  The more data that's being transfered the more CPU usage there will be.

# Pre-reqs:
```
yum install samaba-client
```

if not already part of an AD Domain:
```
realm join <ad domain>
```
  
Create a kerberos ticket.
```
kinit <username>
```
  
In order to scale past 300 connections, you will need to increase your open file limit and run as root.  We need 3 open files per connection to redirect stdin, stdout, & stderr
```
ulimit -n 100000
```
  
# example
```
root@mrstorcycle01 smbtorture]# python3 pysmbtorture.py --server dfwlab-data-1.dfwlab.purestorage.com --share mr-smb1 -t 8000 --cleanup
Connection Count: 100
Connection Count: 200
Connection Count: 300
Connection Count: 400
```

  


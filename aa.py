#!/usr/bin/env python

import netsnmp
import sys
import re

for ipr in ("172.16.99.","172.16.9."):
    for i in range(254):
        ip = ipr+str(i+1)
        st=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.1.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
        if st:
	    if st[:8] == "RouterOS":
                d_type        = st[9:]
                d_software    = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.14988.1.1.4.4.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
                d_bootrom     = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.14988.1.1.7.4.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
                d_hardware    = "RouterOS"
                d_sn          = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.14988.1.1.7.3.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
                d_hostname    = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.5.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
		d_syslocation = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.6.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
                d_uptime      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.3.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
                d_cpumac      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.2.2.1.6.1"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
                d_cpumac      = ":".join("{:02x}".format(ord(c)) for c in d_cpumac)
                print "insert into SWITCHES values(datetime('now','+3 Hour'),'%s','%s','%s','%s','%s','%s','%s','%s','%s',%s);"%(ip,d_type,d_sn,d_cpumac,d_software,d_hardware,d_bootrom,d_hostname,d_syslocation,d_uptime)

#!/usr/bin/env python
# -*- coding: UTF8 -*-
#---------------------------------------------------------------------------------------------------------------------------------------
#import telnetlib
import netsnmp
import sqlite3
#import urllib
#import pprint
#import sys
#import cgi
#import cgi
#import os
import re
#---------------------------------------------------------------------------------------------------------------------------------------
con = sqlite3.connect("/tmp/OLT.db")
con.execute("""create table if not exists SWITCHES (
    datetime datetime,
    ip text,
    devicetype text,
    sn text,
    cpumac text,
    software text,
    hardware text,
    bootrom text,
    hostname text,
    syslocation text,
    uptime int
)""")
for i in range(254):
    ip = "172.16.99."+str(i+1)
    st=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.1.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
    if st:
	print ip,st
	if st[:3]=="QSW":
	    d_type        = st.split()[0]
	    d_software    = re.search("SoftWare Version ([\d\.]+)",st).group(1)
	    d_bootrom     = re.search("BootRom Version ([\d\.]+)",st).group(1)
	    d_hardware    = re.search("HardWare Version ([\w\.]+)",st).group(1)
	    d_sn          = re.search("Device serial number (\d+)",st).group(1)
	    d_hostname    = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.5.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
	    d_syslocation = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.6.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
	    d_uptime      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.3.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
	    d_cpumac      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.2.2.1.6.3099"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
	    d_cpumac      = ":".join("{:02x}".format(ord(c)) for c in d_cpumac)
	    con.execute("insert into SWITCHES values(datetime('now','+3 Hour'),'%s','%s','%s','%s','%s','%s','%s','%s','%s',%s)"%(ip,d_type,d_sn,d_cpumac,d_software,d_hardware,d_bootrom,d_hostname,d_syslocation,d_uptime))
con.commit()
con.close()

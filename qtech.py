#!/usr/bin/env python
# -*- coding: UTF8 -*-
#---------------------------------------------------------------------------------------------------------------------------------------
import time
import telnetlib
import netsnmp
import sqlite3
import pymongo
#---------------------------------------------------------------------------------------------------------------------------------------
dbfile="/opt/OLT/OLT.db"
curentfw="B01D002P006"
#---------------------------------------------------------------------------------------------------------------------------------------
def setZN(sn,ZNtxt,zn):
    try:
	con = pymongo.Connection()
	db = con.OLT
	if not db.onts.find_one({'sn':sn}):
	    db.onts.save({ 'sn':sn,ZNtxt:zn})
	else:
	    ont=db.onts.find_one({'sn':sn})
	    ont[ZNtxt]=zn
	    db.onts.save(ont)
    except: pass
#---------------------------------------------------------------------------------------------------------------------------------------
class SW:
    def __init__(self,ip,user,pw,dbw=1):
	self.ip=ip
	self.dbw=dbw
	self.tn=telnetlib.Telnet(ip)
	self.tn.read_until("login:")
	self.tn.write(user+"\n")
	self.tn.read_until("Password:")
	self.tn.write(pw+"\n")
	self.tn.read_until("#")
    def __del__(self):
	self.tn.write("exit\n")
    def saveConf(self,):
	self.runCMD("copy running-config startup-config\n")
    def createVlan(self,vlanid,vlandescr):
	self.runCMD("conf\n")
	self.runCMD("vlan "+str(vlanid)+"\n")
	self.runCMD("name "+str(vlandescr)+"\n")
	self.runCMD("exit\n")
    def runCMD(self,cmd):
	self.tn.write(cmd)
	self.txt = self.tn.read_until("#",1)
	while self.txt[-1]<>"#":
	    self.tn.write("y\n")
	    self.txt += self.tn.read_until("#",1)
	self.txt =self.txt.replace("".join(chr(c) for c in [0x20,0x1b,0x5b,0x37,0x34,0x44,0x1b,0x5b,0x4b]),"\r\n")
	return self.txt
#---------------------------------------------------------------------------------------------------------------------------------------
class OLT:
    def __init__(self,ip,user,pw,dbw=1):
	self.ip=ip
	self.abonvlan=int(self.ip.split(".")[3])
	self.dbw=dbw
	self.tn=telnetlib.Telnet(ip)
	self.tn.read_until("Username(1-32 chars):")
	self.tn.write(user+"\n")
	self.tn.read_until("Password(1-16 chars):")
	self.tn.write(pw+"\n")
	self.tn.read_until(">")
	self.tn.write("en\n")
	self.tn.read_until("#")
    def __del__(self):
	self.tn.write("exit\n")
	self.tn.read_until(">")
	self.tn.write("exit\n")
    def createVlan(self,vlanid,vlandescr):
	self.goConf()
	self.runCMD("vlan "+str(vlanid)+"\n")
	self.runCMD("description "+str(vlandescr)+"\n")
	self.exitOnce()
	self.exitOnce()
    def runCMD(self,cmd):
	self.tn.write(cmd)
	self.txt = self.tn.read_some()
	while self.txt[-1] not in ("#",">"):
	    self.tn.write(" \n")
	    self.txt += self.tn.read_until("#",1)
	self.txt =self.txt.replace("".join(chr(c) for c in [0x1b,0x5b,0x37,0x33,0x44,0x1b,0x5b,0x4b]),"\r\n")
#	self.txt =self.txt.replace("".join(chr(c) for c in [0x20,0x1b,0x5b,0x37,0x34,0x44,0x1b,0x5b,0x4b]),"\r\n")
	return self.txt
    def showONTBriefOldDead(self):
	self.tn.write("show ont brief\n")
	self.txt = self.tn.read_until("#",1)
	while self.txt[-1]<>"#":
	    self.tn.write(" \n")
	    self.txt += self.tn.read_until("#",1)
	self.itog={}
	#print self.txt
	self.txt =self.txt.replace("".join(chr(c) for c in [0x1b,0x5b,0x37,0x33,0x44,0x1b,0x5b,0x4b]),"\r\n")
#	self.txt =self.txt.replace("".join(chr(c) for c in [0x20,0x1b,0x5b,0x37,0x34,0x44,0x1b,0x5b,0x4b]),"\r\n")
	for i in self.txt.split("\r\n"):
	    if i[0:2]=="0/":
		self.itog[i.split()[0]]=[i.split()[1],i.split()[2],i.split()[6]]
	self.tn.read_until("#",1)
	if self.dbw:
	    con = sqlite3.connect(dbfile)
	    con.execute("create table if not exists ONT (dt datetime,ip text,sn text,num text,status text,error text,rssi real,temp real,uptime datetime,distance int,descr text,swversion text)")
	    con.execute("create index if not exists ONTSNDT on ONT (dt,sn)")
	for i in self.itog:
	    rssi=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.22."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    temp=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.24."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    uptime=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.19."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    distance=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.32."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    descr=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.25."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    try:
		fwver=unicode(netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.12."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0])
	    except:
		fwver="Error"
	    self.itog[i]=self.itog[i]+[str(rssi),str(temp),str(uptime),str(distance),str(descr),str(fwver)]
	    try:
		uptime = int(uptime.split()[0].replace("Day",""))*24*60 + int(uptime.split()[1].replace("Hour",""))*60 + int(uptime.split()[2].replace("Minute",""))
	    except:
		uptime = 0
	    if not temp or temp == "-":
		temp = 0
	    if not rssi or rssi == "-":
		rssi = -30
	    try: 
		int(distance)*2
	    except:
		distance = 0
	    if self.dbw:
		con.execute("insert into ONT values(datetime('now','+3 Hour'),'%s','%s','%s','%s','%s',%s,%s,%s,%s,'%s','%s')"%(self.ip,self.itog[i][0],i,self.itog[i][1],self.itog[i][2],rssi,temp,uptime,distance,descr,fwver))
	if self.dbw:
	    con.commit()
	    con.close()
	return self.itog
    def showONTBrief(self):
	self.itog={}
	var=netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.2")
	while 1:
	    res=netsnmp.snmpgetnext(var,Version=2,DestHost=self.ip,Community="public")
	    if var.tag.split(".")[-4]<>"2":
		break
	    num=var.tag.split(".")[-3]+"/"+var.tag.split(".")[-2]+"/"+var.tag.split(".")[-1]
#	    print num,var.tag,res
	    self.itog[num]=[res[0]]
	    var=netsnmp.Varbind(var.tag)
	if self.dbw:
	    con = sqlite3.connect(dbfile)
	    con.execute("create table if not exists ONT (dt datetime,ip text,sn text,num text,status text,error text,rssi real,temp real,uptime datetime,distance int,descr text,swversion text)")
	    con.execute("create index if not exists ONTSNDT on ONT (dt,sn)")
	for i in self.itog:
	    status=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.3."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    if status=="1": 
		status="online" 
	    else: 
		status="offline"
	    lasterror=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.7."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    if lasterror=="0": lasterror="power"
	    if lasterror=="1": lasterror="----"
	    if lasterror=="2": lasterror="los"
	    if lasterror=="4": lasterror="lofi"
	    if lasterror=="6": lasterror="sf"
	    if lasterror=="212": lasterror="deactivated"
	    rssi=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.22."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    temp=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.24."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    uptime=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.19."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    distance=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.32."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    descr=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.25."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0]
	    try:
		fwver=unicode(netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.27514.1.11.4.1.1.12."+i.replace("/",".")),Version=2,DestHost=self.ip,Community="public")[0])
	    except:
		fwver="Error"
	    self.itog[i]=self.itog[i]+[status,lasterror,str(rssi),str(temp),str(uptime),str(distance),str(descr),str(fwver)]
	    try:
		uptime = int(uptime.split()[0].replace("Day",""))*24*60 + int(uptime.split()[1].replace("Hour",""))*60 + int(uptime.split()[2].replace("Minute",""))
	    except:
		uptime = 0
	    if not temp or temp == "-":
		temp = 0
	    if not rssi or rssi == "-":
		rssi = -30
	    try: 
		int(distance)*2
	    except:
		distance = 0
	    setZN(self.itog[i][0],'ip',self.ip)
	    setZN(self.itog[i][0],'num',i)
	    setZN(self.itog[i][0],'status',self.itog[i][1])
	    setZN(self.itog[i][0],'error',self.itog[i][2])
	    setZN(self.itog[i][0],'rssi',rssi)
	    setZN(self.itog[i][0],'temp',temp)
	    setZN(self.itog[i][0],'uptime',uptime)
	    setZN(self.itog[i][0],'dist',distance)
	    setZN(self.itog[i][0],'descr',descr)
	    setZN(self.itog[i][0],'fwver',fwver)
	    setZN(self.itog[i][0],'time',time.time())
	    if self.dbw:
		con.execute("insert into ONT values(datetime('now','+3 Hour'),'%s','%s','%s','%s','%s',%s,%s,%s,%s,'%s','%s')"%(self.ip,self.itog[i][0],i,self.itog[i][1],self.itog[i][2],rssi,temp,uptime,distance,descr,fwver))
	if self.dbw:
	    con.commit()
	    con.close()
	return self.itog
    def showONTConf(self,ont):
	self.tn.write("show running-config ontmnt "+ont+"\n")
	conf = self.tn.read_until("#",3)
	try:
	    sn = conf[conf.find("sn"):].split()[2]
	    if self.dbw:
		con = sqlite3.connect(dbfile)
		con.execute("create table if not exists ONTConf (dt datetime,ip text,sn text,num text,conf text);")
		con.execute("insert into ONTConf values(datetime(),'%s','%s','%s','%s');"%(ip,sn,ont,conf))
		con.commit()
		con.close()
	except: pass
	return conf
    def showMAConONT(self,ont):
	self.tn.write("show mac-address-table ont "+ont+"\n")
	return self.tn.read_until("#",3)
    def showONTStat(self,ont):
	self.tn.write("show ont status "+ont+"\n")
	return self.tn.read_until("#",3)
    def showONTEthStat(self,ont):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#",1)
	self.tn.write("show ethernet state\n")
	res = self.tn.read_until("#",3)
	self.exitOnce()
	self.exitOnce()
	return res
    def uploadFW(self):
	#self.tn.write("load ont-image tftp inet 172.16.99.11 gpon/ont4.u\n")
	self.tn.write("load ont-image ftp inet 172.16.99.11 gpon/ont4.u ftp ftp\n")
	self.tn.read_until("#")
    def saveConf(self):
	self.goConf()
	self.tn.write("interface range pon 0/1 to pon 0/8\n")
	self.tn.read_until("#")
	self.tn.write("save ont-auto-config\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
	self.tn.write("copy running-config startup-config\n")
	self.tn.read_until("[n]")
	self.tn.write("y\n")
	self.tn.read_until("#")
    def ONTReboot(self,ont):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("ont-reboot\n")
	self.tn.read_until("[n]")
	self.tn.write("y\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
    def ONTUpdateFW(self,ont):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("ont-update-omci\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
    def goConf(self):
	self.tn.write("configure terminal\n")
	self.tn.read_until("#")
    def setONTDescr(self,ont,descr):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("description "+descr+"\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
    def exitOnce(self):
	self.tn.write("exit\n")
	self.tn.read_until("#")
#    def setONTVlans(self,ont):
#	self.goConf()
#	self.tn.write("ont "+ont+"\n")
#	self.tn.read_until("#")
#	self.tn.write("service-port 1\n")
#	self.tn.read_until("#")
#	self.tn.write("vlan 35,99,100,%s\n"%(self.abonvlan))
#	self.tn.read_until("#")
#	self.exitOnce()
#	self.exitOnce()
#	self.exitOnce()
    def setONTDefConf(self,ont):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("tcont 1\n")
	self.tn.read_until("#")
	self.tn.write("gemport 1\n")
	self.tn.read_until("#")
	self.tn.write("bind profile dba name FOX_DBA_MAX\n")
	self.exitOnce()
	self.tn.read_until("#")
	self.tn.write("service-port 1\n")
	self.tn.read_until("#")
	self.tn.write("mapping gemport 1\n")
	self.tn.read_until("#")
	self.tn.write("vlan 35,"+str(self.abonvlan)+"\n")
	self.tn.read_until("#")
	self.setONTIfAcessVlan(ont,1,self.abonvlan)
	self.setONTIfAcessVlan(ont,2,self.abonvlan)
	self.setONTIfAcessVlan(ont,3,self.abonvlan)
	self.setONTIfAcessVlan(ont,4,self.abonvlan)
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("service-port 1\n")
	self.tn.read_until("#")
	self.tn.write("no vlan 9,34,66,99,100,200,201,\n")
	self.exitOnce()
	self.exitOnce()
	self.exitOnce()
    def setONTIfAcessVlan(self,ont,interface,vlan):
	if vlan==0: vlan=int(self.abonvlan)
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("service-port 1\n")
	self.tn.read_until("#")
	self.tn.write("vlan "+str(vlan)+"\n")
	self.tn.read_until("#")
	self.tn.write("exit\n")
	self.tn.read_until("#")
	self.tn.write("interface ethernet 0/"+str(interface)+"\n")
	self.tn.read_until("#")
	self.tn.write("vlan mode tagged\n")
	self.tn.read_until("#")
	self.tn.write("tagged vlan "+str(vlan)+"\n")
	self.tn.read_until("#")
	if vlan>=100 and vlan<=198:
	    self.tn.write("downstream-igmp-and-multicast-tci control-type 1 vlan 35\n")
	    self.tn.read_until("#")
	else:
	    self.tn.write("no downstream-igmp-and-multicast-tci\n")
	    self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
	self.exitOnce()
    def setONTIfTrunk(self,ont,interface):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("service-port 1\n")
	self.tn.read_until("#")
	self.tn.write("vlan 9,35,99,100,201\n")
	self.tn.read_until("#")
	self.tn.write("exit\n")
	self.tn.read_until("#")
	self.tn.write("interface ethernet 0/"+str(interface)+"\n")
	self.tn.read_until("#")
	self.tn.write("no downstream-igmp-and-multicast-tci\n")
	self.tn.read_until("#")
	self.tn.write("vlan mode transparent\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
	self.exitOnce()
    def setONTIfOn(self,ont,interface):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("interface ethernet 0/"+str(interface)+"\n")
	self.tn.read_until("#")
	self.tn.write("no shutdown\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
	self.exitOnce()
    def setONTIfOff(self,ont,interface):
	self.goConf()
	self.tn.write("ont "+ont+"\n")
	self.tn.read_until("#")
	self.tn.write("interface ethernet 0/"+str(interface)+"\n")
	self.tn.read_until("#")
	self.tn.write("shutdown\n")
	self.tn.read_until("#")
	self.exitOnce()
	self.exitOnce()
	self.exitOnce()
#---------------------------------------------------------------------------------------------------------------------------------------
#o=OLT("172.16.199.119","admin","password",0)
#ontbrief=o.showONTBrief()
#pprint.pprint(ontbrief)
#addSNMPData(ontbrief,"172.16.199.119","public")
#pprint.pprint(ontbrief)
#o.setONTDefConf("0/2/10")
#o.setONTDescr("0/2/10","test")
#o.setONTIfAcessVlan("0/2/10",1,34)
#o.setONTIfAcessVlan("0/2/10",2,100)
#o.setONTIfAcessVlan("0/2/10",3,200)
#o.setONTIfAcessVlan("0/2/10",4,99)
#o.setONTIfTrunk("0/2/10",4)
#o.uploadFW()
#o.ONTUpdateFW("0/2/10")
#o.ONTReboot("0/2/10")
#print o.showONTConf("0/2/10")
#o.saveConf()
#---------------------------------------------------------------------------------------------------------------------------------------

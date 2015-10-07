#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import syslog
import sqlite3
import pymongo
dbfile="/opt/OLT/OLT.db"
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
df=open("/tmp/ontsyslog","a")
while True:
    line = sys.stdin.readline()
    df.write(line)
    if line:
	pos=line.lower().find("qtec1")
	if pos>-1:
	    try:
		num=line[:pos].split()[-1]
		ip=line.split()[1]
		sn=line[pos:].split()[0]
		st=line[pos:].split()[1]
		con = sqlite3.connect(dbfile)
		df.write(sn+" ")
		df.write(num+" ")
		df.write(ip+" ")
		df.write(st+" \n")
		df.flush()
		if st=="register":
		    setZN(sn,'ip',ip)
		    setZN(sn,'num',num)
		    setZN(sn,'error','----')
		    setZN(sn,'status','online')
		    setZN(sn,'time',time.time())
		    con.execute("insert into ONT values(datetime('now','+3 Hour'),'%s','%s','%s','online','----',-30,0,0,0,'','')"%(ip,sn,num))
		else:
		    setZN(sn,'ip',ip)
		    setZN(sn,'num',num)
		    setZN(sn,'error',st)
		    setZN(sn,'status','offline')
		    setZN(sn,'time',time.time())
		    con.execute("insert into ONT values(datetime('now','+3 Hour'),'%s','%s','%s','offline','%s',-30,0,0,0,'','')"%(ip,sn,num,st))
		con.commit()
		con.close()
	    except:
		pass
    else:
      break
df.close()
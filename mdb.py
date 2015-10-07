#!/usr/bin/env python
# -*- coding: UTF8 -*-

import pymongo
import datetime

def tp(o,st):
    try: return o[st]
    except: return "Null"

def setZN(sn,ZNtxt,zn):
    con = pymongo.Connection()
    db = con.OLT
    if not db.onts.find_one({'sn':sn}):
	db.onts.save({ 'sn':sn,ZNtxt:zn})
    else:
	ont=db.onts.find_one({'sn':sn})
	ont[ZNtxt]=zn
	db.onts.save(ont)
def prTL(i,j):
    if tp(i,'status')=="offline":
	print "<tr bgcolor=red>",
    else:
	print "<tr>",
    print "<td>",j,"</td>",
    print "<td>",tp(i,'ip'),"</td>",
    print "<td>",tp(i,'sn'),"</td>",
    print "<td>",tp(i,'descr'),"</td>",
    print "<td>",tp(i,'num'),"</td>",
    print "<td>",tp(i,'status'),"</td>",
    print "<td>",tp(i,'error'),"</td>",
    print "<td>",tp(i,'rssi'),"</td>",
    print "<td>",tp(i,'temp'),"</td>",
    print "<td>",tp(i,'uptime'),"</td>",
    print "<td>",tp(i,'dist'),"</td>",
    print "<td>",tp(i,'fwver'),"</td>",
    if tp(i,'time')<>"Null":
	print "<td>", datetime.datetime.fromtimestamp(tp(i,'time')).strftime('%Y-%m-%d %H:%M:%S'),"</td>",
    print "</tr>"

print "Content-type: text/html"
print
print "<html>"
print """<head>
<style>
 body {
    <!--background-image: url(/img/1.jpg);-->
    color :#ff7777;
    background-color: #c7b39b;
    -webkit-background-size: cover;
    -moz-background-size: cover;
    -o-background-size: cover;
    background-size: cover;
   }
 h1 {
    color: #00ff00;
 }
</style>
<meta http-equiv="refresh" content="50">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>"""
print "<body>"
#print "<h1>Dали нахрен спать! дай поработать!</h1>"
print "Таблица ONT в Offline"
print "<table border=1>"
j=1
for i in pymongo.Connection().OLT.onts.find({"status": 'offline'}).sort([["time",-1],["num",1]]):
    prTL(i,j)
    j=j+1
j=1
print"</table><br>"

print "Таблица ONT Радио Левобережное"
print"<table border=1>"
j=1
for i in pymongo.Connection().OLT.onts.find().sort([["ip",1],["num",1]]):
    if i['sn'].replace("QTEC","").replace("qtec","") in ("14050183","14050458","14050146","14030247","14030135","14030508","14030399","14030635","14030370","14030010"):
	prTL(i,j)
	j=j+1
print "</table><br>"

print "Таблица всех ONT"
print "<table border=1>"
for i in pymongo.Connection().OLT.onts.find().sort([["ip",1],["num",1]]):
    prTL(i,j)
    j=j+1
print "</table>"
print "</body>"
print "</html>"
#!/usr/bin/env python
# -*- coding: UTF8 -*-
import os
from qtech import *

def showONTTable(ip,user,password):
    o=OLT(ip,user,password)
    ontbrief=o.showONTBrief()
    if len(ontbrief)==0:
	print "<h1><font color='red'>На Этой ОЛТ нет ни одной ОНТ!!!!!</font></h1>"
	print "<h1><font color='red'>P.S.</font></h1>"
	print "<h1><font color='red'>Сварщик врет. Если я сказал нет - значит НЕТ!</font></h1>"
    print "<table border=1>"
    for i in sorted(ontbrief):
	color="#aaaaaa"
	if ontbrief[i][1]=="online":
	    color="#55ff55"
	if ontbrief[i][3]=="-30.0000" and ontbrief[i][4]=="0.00":
	    color="pink"
	if ontbrief[i][3]=="-" and ontbrief[i][4]=="-":
	    color="yellow"
	if ontbrief[i][1]=="offline":
	    color="#ff0000"
	print "<tr bgcolor="+color+">"
	print "<td><a href=?oltip="+ip+"&ont="+i+"&cmd=showont>"+i+"</a></td>"
	print "<td><a href=?cmd=showontbysn&descr=%s>%s</td>"%(ontbrief[i][0],ontbrief[i][0])
	print "<td>"+ontbrief[i][1]+"</td>"
	print "<td>"+ontbrief[i][2]+"</td>"
	print "<td>"+ontbrief[i][3]+"</td>"
	print "<td>"+ontbrief[i][4]+"</td>"
	print "<td>"+ontbrief[i][5]+"</td>"
	print "<td>"+ontbrief[i][6]+"</td>"
	print "<td>"+ontbrief[i][7]+"</td>"
	print "<td>"+ontbrief[i][8]+"</td>"
	if ontbrief[i][1]=="online":
	    print "<td><a href='?oltip="+ip+"&ont="+i+"&cmd=rebootont'>Перезагрузить ONT</a></td>"
	if ontbrief[i][8]<>curentfw and ontbrief[i][3]<>"-":
	    print "<td>"
	    print "<a href='?oltip="+ip+"&ont="+i+"&cmd=updatefw'>Обновить прошивку</a>"
	    print "</td>"
	print "</tr>"
    print "</table>"



print "Content-type: text/html"
print
print "<HTML>"
print "<HEAD>"
print "</HEAD>"
print "<body>"
#print os.environ['REMOTE_USER']

showONTTable("172.168.199.5","user","password")

print "</body>"
print "</HTML>"

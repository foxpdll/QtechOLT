#!/usr/bin/env python
# -*- coding: UTF8 -*-
#---------------------------------------------------------------------------------------------------------------------------------------
from qtech import *
import telnetlib
import netsnmp
import sqlite3
import urllib
import pprint
import sys
import cgi
import cgi
import re
import os
sys.stderr = open('/tmp/err.txt', 'w')
#"create view if not exists ONTLast as select * from ONT group by 3,2 order by 2,4;"
#---------------------------------------------------------------------------------------------------------------------------------------
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
#---------------------------------------------------------------------------------------------------------------------------------------
def lockMe():
    try: ru=os.environ['REMOTE_USER']
    except: ru="Anonymous"
    con = sqlite3.connect(dbfile)
    con.execute("""create table if not exists LOCK (datetime datetime, user text)""")
    for i in con.execute("select strftime('%s',datetime('now','+3 Hour'))-strftime('%s',max(datetime)),user from LOCK"):
	if i[0] and i[0]<60:
	    print "<meta http-equiv='refresh' content='5;'></head>"
	    print "<H1>Приложение занято пользователем. Обратитесь попозже!</H1>"
	    print i[0],i[1]
	    print "</html>"
	    sys.exit()
    con.execute("insert into LOCK values(datetime('now','+3 Hour'),'%s')"%(ru))
    con.commit()
    con.close()
#---------------------------------------------------------------------------------------------------------------------------------------
def unlockMe():
    con = sqlite3.connect(dbfile)
#    con.execute("""create table if not exists LOCK (datetime datetime)""")
    con.execute("""drop table if exists LOCK""")
    con.commit()
    con.close()
#---------------------------------------------------------------------------------------------------------------------------------------
#o=OLT("172.16.199.119","admin","password")
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
#sys.exit()
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------
ip=""
ont=""
cmd=""
olts={
      "172.16.199.191":("ПС00 ЦУ OLT 1","admin","password"),
      "172.16.199.190":("ПС00 ЦУ OLT 2","admin","password"),
      "172.16.199.197":("ПС01 Ворошилова31а","admin","password"),
      "172.16.199.195":("ПС02_1 Беговая2/3","admin","password"),
      "172.16.199.108":("ПС02_2 Беговая2/3(Бывшая КУ08)","admin","password"),
      "172.16.199.193":("ПС03_1 Лизюкова","admin","password"),
      "172.16.199.192":("ПС03_2 Лизюкова","admin","password"),
      "172.16.199.106":("КУ06","admin","password"),
      "172.16.199.107":("КУ07","admin","password"),
      "172.16.199.109":("КУ09","admin","password"),
      "172.16.199.110":("КУ10","admin","password"),
      "172.16.199.112":("КУ12","admin","password"),
      "172.16.199.115":("КУ15","admin","password"),
      "172.16.199.119":("КУ19","admin","password"),
      "172.16.199.120":("КУ20","admin","password"),
      "172.16.199.122":("КУ22","admin","password"),
      "172.16.199.126":("КУ26","admin","password"),
      "172.16.199.186":("КУ26-2","admin","password"),
      "172.16.199.129":("КУ29","admin","password"),
      "172.16.199.189":("КУ29-2","admin","password"),
      "172.16.199.130":("КУ30","admin","password"),
      "172.16.199.133":("КУ33","admin","password"),
      "172.16.199.183":("КУ33-2","admin","password"),
      "172.16.199.136":("КУ36","admin","password"),
      "172.16.199.137":("КУ37","admin","password"),
      "172.16.199.138":("КУ38","admin","password"),
      "172.16.199.188":("КУ38-2","admin","password"),
      "172.16.199.140":("КУ40","admin","password"),
      "172.16.199.152":("КУ52","admin","password"),
      "172.16.199.154":("КУ54","admin","password"),
      "172.16.199.155":("КУ55","admin","password"),
      "172.16.199.158":("КУ58","admin","password")
}
#---------------------------------------------------------------------------------------------------------------------------------------
arguments = cgi.FieldStorage()
for i in arguments.keys():
    if i=="oltip": ip=arguments[i].value
    if i=="descr": descr=arguments[i].value
    if i=="vlan": vlan=arguments[i].value
    if i=="ont": ont=arguments[i].value.replace(".","/")
    if i=="cmd": cmd=arguments[i].value
print "Content-type: text/html"
print
print "<HTML>"
print "<HEAD>"
print """<style>
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
</style>"""
print '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
lockMe()
try:
    if cmd=="showmap":
	print"""
	<title>Карта OLT</title>
	<script src="http://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
	<script src="http://yandex.st/jquery/2.1.0/jquery.min.js" type="text/javascript"></script>
	<style>
	    html, body, #map {
	        width: 100%; height: 100%; padding: 0; margin: 0;
	    }
	</style>
	<script type="text/javascript">
	ymaps.ready(init);
	function init () {
	    var myMap = new ymaps.Map('map', {
	            center: [51.67, 39.22],
	            zoom: 12
	        }),
	        objectManager = new ymaps.ObjectManager({
	            clusterize: true,
	            gridSize: 32
	        });
	    myMap.geoObjects.add(objectManager);
	"""
	o=OLT(ip,olts[ip][1],olts[ip][2])
	ontbrief=o.showONTBrief()
	for i in ontbrief:
	    ont_pnum=i
	    ont_sn=ontbrief[i][0]
	    ont_rssi=ontbrief[i][3]
	    ont_temp=ontbrief[i][4]
	    ont_uptime=ontbrief[i][5]
	    ont_dist=ontbrief[i][6]
	    ont_descr=ontbrief[i][7]
	    color="green"
	    if ont_rssi=="-" and ont_temp=="-":
		color="yellow"
	    if ont_rssi=="-30.0000" and ont_temp=="0.00":
		color="pink"
	    if ont_rssi=="-" and ont_temp=="-" and ont_uptime=="-" and ont_dist=="-":
		color="red"
	    print """
	    ymaps.geocode('Россия, Воронеж, %s',{results: 1}).then(function (res) {
	    var firstGeoObject = res.geoObjects.get(0),
	    coords = firstGeoObject.geometry.getCoordinates(), 
	    bounds = firstGeoObject.properties.get('boundedBy');
	    var myPlacemark = new ymaps.Placemark(coords, {
	        iconContent: '%s',
	        balloonContent: 'Россия, Воронеж, %s'
	    },{
	        preset: 'islands#%sStretchyIcon'
	    });
	    myMap.geoObjects.add(myPlacemark);
	    });"""%(ont_descr.replace("!","").split("_")[0],ont_rssi,ont_descr+" "+ont_sn+" "+ont_pnum,color)
	print """
	}
        </script>
	"""
	print "</HEAD>"
    if cmd=="showont":
	print "</HEAD>Конфигурация ONT "+ont+" on ip "+ip+"<br>"
	print "<pre>"
	olt=OLT(ip,olts[ip][1],olts[ip][2])
	print olt.showONTConf(ont)
	ontstatus=olt.showONTStat(ont)
	print ontstatus
	print olt.showMAConONT(ont)
	print olt.showONTEthStat(ont)

	try:
	    ont_sn = ontstatus.split()[10].split("/")[0][4:]
	    print urllib.urlopen("http://172.16.99.24:7171/getContractByDeviceId?identifier=%s" % ont_sn).read()
	except: pass
	print "</pre>"
	print """
	<form>
	    <input type="hidden" name=oltip value="%s">
	    <input type="hidden" name=ont value="%s">
	    <input type="hidden" name=cmd value="setontdef">
	    <table border=1>
		<tr><td>Первоначальная настройка ОНТ </td>
		<td><input type="submit" value="Настроить"></td></tr>
	    </table>
	</form>
	<form>
	    <input type="hidden" name=oltip value="%s">
	    <input type="hidden" name=ont value="%s">
	    <input type="hidden" name=cmd value="updateontdescr">
	    <table border=1>
		<tr><td>Описание:</td>
		<td><input name="descr" type="text"></td>
		<td><input type="submit" value="Изменить"></td></tr>
	    </table>
	</form>
	<form>
	    <input type="hidden" name=oltip value="%s">
	    <input type="hidden" name=ont value="%s">
	    <input type="hidden" name=cmd value="setport1">
	    <table border=1>
		<tr><td>Интерфейс1:</td><td>
		    <input type="radio" name="vlan" value="0">Физическое лицо
		    <input type="radio" name="vlan" value="34">Мониторинг Телевизионного оборудования
		    <input type="radio" name="vlan" value="trunk">Транковый порт для Свича
		    <input type="radio" name="vlan" value="shuton">Включить порт
		    <input type="radio" name="vlan" value="shutoff">Выключить порт
		</td><td>
		    <input type="submit" value="Изменить">
		</td></tr>
	    </table>
	</form>
	<form>
	    <input type="hidden" name=oltip value="%s">
	    <input type="hidden" name=ont value="%s">
	    <input type="hidden" name=cmd value="setport2">
	    <table border=1>
		<tr><td>Интерфейс2:</td><td>
		    <input type="radio" name="vlan" value="0"hecked>Физическое лицо
		    <input type="radio" name="vlan" value="34">Мониторинг Телевизионного оборудования
		    <input type="radio" name="vlan" value="trunk">Транковый порт для Свича
		    <input type="radio" name="vlan" value="shuton">Включить порт
		    <input type="radio" name="vlan" value="shutoff">Выключить порт
		</td><td>
		    <input type="submit" value="Изменить">
		</td></tr>
	    </table>
	</form>
	<form>
	    <input type="hidden" name=oltip value="%s">
	    <input type="hidden" name=ont value="%s">
	    <input type="hidden" name=cmd value="setport3">
	    <table border=1>
		<tr><td>Интерфейс3:</td><td>
		    <input type="radio" name="vlan" value="0">Физическое лицо
		    <input type="radio" name="vlan" value="34">Мониторинг Телевизионного оборудования
		    <input type="radio" name="vlan" value="trunk">Транковый порт для Свича
		    <input type="radio" name="vlan" value="shuton">Включить порт
		    <input type="radio" name="vlan" value="shutoff">Выключить порт
		</td><td>
		    <input type="submit" value="Изменить">
		</td></tr>
	    </table>
	</form>
	<form>
	    <input type="hidden" name=oltip value="%s">
	    <input type="hidden" name=ont value="%s">
	    <input type="hidden" name=cmd value="setport4">
	    <table border=1>
		<tr><td>Интерфейс4:</td><td>
		    <input type="radio" name="vlan" value="0">Физическое лицо
		    <input type="radio" name="vlan" value="34">Мониторинг Телевизионного оборудования
		    <input type="radio" name="vlan" value="trunk">Транковый порт для Свича
		    <input type="radio" name="vlan" value="shuton">Включить порт
		    <input type="radio" name="vlan" value="shutoff">Выключить порт
		</td><td>
		    <input type="submit" value="Изменить">
		</td></tr>
	    </table>
	</form>
	"""%(ip,ont.replace("/","."),ip,ont.replace("/","."),ip,ont.replace("/","."),ip,ont.replace("/","."),ip,ont.replace("/","."),ip,ont.replace("/","."))
    if cmd=="setport1":
	print "<script>history.go(-1)</script>></head>"
	try:
	    OLT(ip,olts[ip][1],olts[ip][2]).setONTIfAcessVlan(ont,1,int(vlan))
	except:
	    if vlan=="trunk": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfTrunk(ont,1)
	    if vlan=="shuton": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOn(ont,1)
	    if vlan=="shutoff": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOff(ont,1)
    if cmd=="setport2":
	print "<script>history.go(-1)</script>></head>"
	try:
	    OLT(ip,olts[ip][1],olts[ip][2]).setONTIfAcessVlan(ont,2,int(vlan))
	except:
	    if vlan=="trunk": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfTrunk(ont,2)
	    if vlan=="shuton": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOn(ont,2)
	    if vlan=="shutoff": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOff(ont,2)
    if cmd=="setport3":
	print "<script>history.go(-1)</script>></head>"
	try:
	    OLT(ip,olts[ip][1],olts[ip][2]).setONTIfAcessVlan(ont,3,int(vlan))
	except:
	    if vlan=="trunk": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfTrunk(ont,3)
	    if vlan=="shuton": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOn(ont,3)
	    if vlan=="shutoff": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOff(ont,3)
    if cmd=="setport4":
	print "<script>history.go(-1)</script>></head>"
	try:
	    OLT(ip,olts[ip][1],olts[ip][2]).setONTIfAcessVlan(ont,4,int(vlan))
	except:
	    if vlan=="trunk": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfTrunk(ont,4)
	    if vlan=="shuton": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOn(ont,4)
	    if vlan=="shutoff": OLT(ip,olts[ip][1],olts[ip][2]).setONTIfOff(ont,4)
    if cmd=="setontdef":
	print "<script>history.go(-1)</script>></head>"
	print "Установка дефолтной конфигурации ОНТ "+ont+" on ip "+ip+"<br>"
	OLT(ip,olts[ip][1],olts[ip][2]).setONTDefConf(ont)
    if cmd=="updateontdescr":
	print "<script>history.go(-1)</script>></head>"
	print "Обновление описания ONT "+ont+" on ip "+ip+"<br>"
	print descr
	OLT(ip,olts[ip][1],olts[ip][2]).setONTDescr(ont,descr)
    if cmd=="updatefw":
	print "<script>history.go(-1)</script>></head>"
	print "Updating firmware on ont "+ont+" on ip "+ip
	OLT(ip,olts[ip][1],olts[ip][2]).ONTUpdateFW(ont)
	print "Started Ok"
	print "<br>"
    if cmd=="uploadontfw":
	print "<script>history.go(-1)</script>></head>"
	print "Загрузка прошивки для ONT on ip "+ip
	OLT(ip,olts[ip][1],olts[ip][2]).uploadFW()
	print "Finished Ok"
	print "<br>"
    if cmd=="saveconfig":
	print "<script>history.go(-1)</script>></head>"
	print "Сохранение конфига OLT on ip "+ip
	OLT(ip,olts[ip][1],olts[ip][2]).saveConf()
	print "Finished Ok"
	print "<br>"
    if cmd=="ont2fisik":
	print "Настройка ONT для использования физическим лицом "+ont+" on ip "+ip
	OLT(ip,olts[ip][1],olts[ip][2]).setONTDefConf(ont)
	print "Finished Ok"
	print "<br>"
    if cmd=="rebootont":
	print "<script>history.go(-1)</script>></head>"
	print "Rebooting ont "+ont+" on ip "+ip
	OLT(ip,olts[ip][1],olts[ip][2]).ONTReboot(ont)
	print "Finished Ok"
	print "<br>"
    if cmd=="showontbysn":
	print """
	<script type="text/javascript" src="https://www.google.com/jsapi"></script>
	<script type="text/javascript">
	  google.load("visualization", "1", {packages:["corechart"]});
	  google.setOnLoadCallback(drawChart);
	  function drawChart() {
	    var data = google.visualization.arrayToDataTable([
	      ['Date', 'RSSI'],"""
	con = sqlite3.connect(dbfile)
	c = con.cursor()
	for i in c.execute("select substr(dt,1,13),avg(rssi) from ONT where sn='%s' group by 1 order by 1;"%(descr)):
#	for i in c.execute("select dt,rssi from ONT where sn='%s' order by 1;"%(descr)):
	    print """['%s',%s],"""%(str(i[0]),str(i[1]))
	print """        ]);
	var options = {
	  title: '%s',
	  hAxis: {title: 'Date',  titleTextStyle: {color: '#333'}},
	  vAxis: {minValue: -30}
	};
	var chart = new google.visualization.AreaChart(document.getElementById('chart_div'));
	chart.draw(data, options);
	}
	</script>
	</head>"""%(descr)
	print """<div id="chart_div" style="width: 900px; height: 500px;"></div>"""
	print "<table border=1>"
	for i in c.execute("select * from ONT where sn='%s' order by 1 desc;"%(descr)):
	    print "<tr>"
	    for j in i:
		print "<td>%s</td>"%(j)
	    print "</tr>"
	print "</table>"
    if cmd=="showswitch":
	print "<h1>Договора на свиче %s</h1>"%(descr)
	print "<pre>"
	print urllib.urlopen("http://172.16.99.24:7171/getContractByDeviceId?identifier=%s" % descr.replace(":","")).read()
	print "</pre>"
    if ip and not cmd:
	#print "<meta http-equiv='refresh' content='60; url=?oltip="+ip+"'></head>"
	print "<a href=?><h1>Главная!</h1></a>"
	print "<a href=?oltip="+ip+"&ont=0.0.0&cmd=showmap>Карта</a><br>"
	print "<a href=?oltip="+ip+"&ont=0.0.0&cmd=saveconfig>Сохранить конфигурацию</a><br>"
	try: showONTTable(ip,olts[ip][1],olts[ip][2])
	except: "Случилась непредвиденная ошибка."
	print "<br><br><br><a href=?oltip="+ip+"&ont=0.0.0&cmd=uploadontfw>Залить прошивку для ONT(Убедитесь что вы понимаете что вы делаете!)</a><br>"
except:
    pass

if not ip and not cmd and len(sys.argv)<2:
    print "</head><a href=?><h1>Главная!</h1></a>"
    for i in sorted(olts.keys()):
	print "<a href=?oltip="+i+">"+olts[i][0]+"</a><br>"
    con = sqlite3.connect(dbfile)
    c = con.cursor()
    print "<h1>Таблица проблемных ONT</h1>"
    print "<table border=1>"
    print "<tr><th>N</th><th>Ку</th><th>SerialN</th><th>Description</th><th>ONT</th><th>Status</th><th>LastError</th><th>RSSI</th><th>Temp</th><th>Uptime</th><th>Distance</th><th>SWVersion</th><th>DataGeted</th></tr>"
    j=0
    c.execute("CREATE VIEW if not exists ONTLast as select * from ONT group by 3,2 order by 2,4;")
    for i in c.execute("select * from ONTLast where status<>'online' and dt >= date('now','-1 hour');"):
	j+=1
	color=""
	if i[11]!= curentfw:
	    color="yellow"
	if i[4]=="offline":
	    color="red"
	print "<tr bgcolor=%s>"%(color)
	print "<td>%s</td>"%(j)
	print "<td><a href=?oltip=%s>%s</td>"%(str(i[1]),olts[i[1]][0])
	print "<td><a href=?cmd=showontbysn&descr=%s>%s</td>"%(i[2],i[2])
	print "<td>"+str(i[10])+"</td>"
	print "<td><a href=?oltip=%s&ont=%s&cmd=showont>%s</td>"%(str(i[1]),str(i[3]),i[3])
	print "<td>"+str(i[4])+"</td>"
	print "<td>"+str(i[5]).replace("----","Все пучком").replace("power","Нет напряжения питания").replace("lofi","Оптический сигнал за пределами нормы").replace("los","Нет оптического сигнала")+"</td>"
	print "<td>"+str(i[6])+"</td>"
	print "<td>"+str(i[7])+"</td>"
	print "<td>"+str(i[8])+"</td>"
	print "<td>"+str(i[9])+"</td>"
	print "<td>"+str(i[11])+"</td>"
	print "<td>"+i[0]+"</td>"
	print "</tr>"
    print "</table>"
    print "<h1>Таблица ONT с запредельными уровнями сигналов</h1>"
    print "<table border=1>"
    print "<tr><th>N</th><th>Ку</th><th>SerialN</th><th>Description</th><th>ONT</th><th>Status</th><th>LastError</th><th>RSSI</th><th>Temp</th><th>Uptime</th><th>Distance</th><th>SWVersion</th><th>DataGeted</th></tr>"
    j=0
    for i in c.execute("select * from ONTLast where (rssi>-10 or rssi<-25) and rssi<>-30 and dt >= date('now','-1 hour');"):
	j+=1
	print "<tr>"
	print "<td>%s</td>"%(j)
	print "<td><a href=?oltip=%s>%s</td>"%(str(i[1]),olts[i[1]][0])
	print "<td><a href=?cmd=showontbysn&descr=%s>%s</td>"%(i[2],i[2])
	print "<td>"+str(i[10])+"</td>"
	print "<td><a href=?oltip=%s&ont=%s&cmd=showont>%s</td>"%(str(i[1]),str(i[3]),i[3])
	print "<td>"+str(i[4])+"</td>"
	print "<td>"+str(i[5]).replace("----","Все пучком").replace("power","Нет напряжения питания").replace("lofi","Оптический сигнал за пределами нормы").replace("los","Нет оптического сигнала")+"</td>"
	print "<td>"+str(i[6])+"</td>"
	print "<td>"+str(i[7])+"</td>"
	print "<td>"+str(i[8])+"</td>"
	print "<td>"+str(i[9])+"</td>"
	print "<td>"+str(i[11])+"</td>"
	print "<td>"+i[0]+"</td>"
	print "</tr>"
    print "</table>"
    print "<h1>Таблица сохраненных данных</h1>"
    print """
<table>
<tr><td bgcolor=red>Жопа</td></tr>
<tr><td bgcolor=yellow>Перепрошивается</td></tr>
<tr><td>Норма</td></tr>
<tr><td bgcolor=magenta>РадиоЛевобережное</td></tr>
<tr><td bgcolor=lightgreen>SFPOnt</td></tr>
</table>
"""
    print "<table border=1>"
    print "<tr><th>N</th><th>Ку</th><th>SerialN</th><th>Description</th><th>ONT</th><th>Status</th><th>LastError</th><th>RSSI</th><th>Temp</th><th>Uptime</th><th>Distance</th><th>SWVersion</th><th>DataGeted</th></tr>"
    j=0
    for i in c.execute("select * from ONT where dt >= date('now','-1 hour') group by 3,2 order by 2,4;"):
	j+=1
	color=""
	if i[11]!= curentfw:
	    color="yellow"
	if i[4]=="offline":
	    color="red"
	tmpbgcolor=""
	if i[2].replace("QTEC","").replace("qtec","") in ("14030370","14030179","14030635","14030304","14030254","14030508","14030399","14030135","14030247","14050589"):
	    tmpbgcolor="magenta"
	if i[2][0:4] in ("SFPA","TWSH"):
	    tmpbgcolor="lightgreen"
	    if color=="yellow": color=""
	print "<tr bgcolor=%s>"%(color)
	print "<td>%s</td>"%(j)
	print "<td><a href=?oltip=%s>%s</td>"%(str(i[1]),olts[i[1]][0])
	print "<td bgcolor=%s><a href=?cmd=showontbysn&descr=%s>%s</td>"%(tmpbgcolor,i[2],i[2])
	print "<td>"+str(i[10])+"</td>"
	print "<td><a href=?oltip=%s&ont=%s&cmd=showont>%s</td>"%(str(i[1]),str(i[3]),i[3])
	print "<td>"+str(i[4])+"</td>"
	print "<td>"+str(i[5]).replace("----","Все пучком").replace("power","Нет напряжения питания").replace("lofi","Оптический сигнал за пределами нормы").replace("los","Нет оптического сигнала")+"</td>"
	print "<td>"+str(i[6])+"</td>"
	print "<td>"+str(i[7])+"</td>"
	print "<td>"+str(i[8])+"</td>"
	print "<td>"+str(i[9])+"</td>"
	print "<td>"+str(i[11])+"</td>"
	print "<td>"+i[0]+"</td>"
	print "</tr>"
    print "</table>"
    print "<br><h1>Switches</h1>"
    print "<table border=1>"
    j=0
    for i in c.execute("select * from SWITCHES group by 2 order by 2"):
	j+=1
	print "<tr>"
	print "<td>%s</td>"%(j)
	print "<td><a href=telnet://%s>%s</td>"%(i[1],i[1])
	print "<td>%s</td>"%(i[3])
	print "<td><a href=?cmd=showswitch&descr=%s>%s</td>"%(i[4],i[4])
	print "<td>%s</td>"%(i[2])
	print "<td>%s</td>"%(i[5])
	print "<td>%s</td>"%(i[6])
	print "<td>%s</td>"%(i[7])
	print "<td>%s</td>"%(i[8])
	print "<td>%s</td>"%(i[9])
	t_d=i[10]/100/60/60/24
	t_h=i[10]/100/60/60-t_d*24
	t_m=i[10]/100/60-t_d*24*60-t_h*60
	t_s=i[10]/100-t_d*24*60*60-t_h*60*60-t_m*60
	print "<td>%.2i дней %.2i:%.2i:%.2i</td>"%(t_d,t_h,t_m,t_s)
	print "<td>%s</td>"%(i[0])
	print "</tr>"
    print "</table>"
    print "Для работы связки протокола telnet сохраните нижеследующий текст как h.reg и запустите:"
    print """<pre>Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\\telnet]
@="URL : Protocol telnet"
"EditFlags"=dword:00000002
"FriendlyTypeName"="@C:\\\\Windows\\\\System32\\\\ieframe.dll,-907"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\\telnet\DefaultIcon]
@="c:\\\\Program Files (x86)\\\\Putty\\\\Putty.exe,0"

[HKEY_CLASSES_ROOT\\telnet\shell]

[HKEY_CLASSES_ROOT\\telnet\shell\open]

[HKEY_CLASSES_ROOT\\telnet\shell\open\command]
@="\\"C:\\\\Program Files (x86)\\\\puTTY\\putty.exe\\" %1"
</pre>"""
    con.close()
print """<body>
<div id="map"></div>
</body>
</HTML>"""

if len(sys.argv)>1:
    if sys.argv[1]=="all":
	try:
	    for i in olts:
		try:
		    print i
		    print OLT(i,olts[i][1],olts[i][2]).showONTBrief()
		except: pass
	except:
	    pass
	try:
	    con = sqlite3.connect(dbfile)
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
    uptime int)""")
	    for ipr in ("172.16.9.","172.16.99."):
		for i in range(254):
		    ip = ipr+str(i+1)
		    st=netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.1.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
		    if st:
			print ip,st
			if st[:8] == "RouterOS":
			    d_type        = st[9:]
			    d_software    = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.14988.1.1.4.4.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_bootrom     = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.14988.1.1.7.4.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_hardware    = "RB"
			    d_sn          = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.4.1.14988.1.1.7.3.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_hostname    = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.5.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_syslocation = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.6.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_uptime      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.3.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_cpumac      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.2.2.1.6.1"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_cpumac      = ":".join("{:02x}".format(ord(c)) for c in d_cpumac)
			    con.execute("insert into SWITCHES values(datetime('now','+3 Hour'),'%s','%s','%s','%s','%s','%s','%s','%s','%s',%s)"%(ip,d_type,d_sn,d_cpumac,d_software,d_hardware,d_bootrom,d_hostname,d_syslocation,d_uptime))
			if st[:3]in ("QSW","SWA"):
			    d_type        = st.split()[0]
			    d_software    = re.search("SoftWare Version ([\d\.]+)",st).group(1)
			    d_bootrom     = re.search("BootRom Version ([\d\.]+)",st).group(1)
			    d_hardware    = re.search("HardWare Version ([\w\.]+)",st).group(1)
			    d_sn          = re.search("serial n.* (\d+)",st.lower()).group(1)
			    d_hostname    = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.5.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_syslocation = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.6.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_uptime      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.1.3.0"),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_cpumac      = netsnmp.snmpget(netsnmp.Varbind(".1.3.6.1.2.1.2.2.1.6."+str(3000+int(ipr.split(".")[-2]))),Version=2,DestHost=ip,Community="public",Timeout=100000)[0]
			    d_cpumac      = ":".join("{:02x}".format(ord(c)) for c in d_cpumac)
			    con.execute("insert into SWITCHES values(datetime('now','+3 Hour'),'%s','%s','%s','%s','%s','%s','%s','%s','%s',%s)"%(ip,d_type,d_sn,d_cpumac,d_software,d_hardware,d_bootrom,d_hostname,d_syslocation,d_uptime))
	    con.commit()
	    con.close()
	except:
	    pass
unlockMe()

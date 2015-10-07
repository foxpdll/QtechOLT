#!/bin/bash

echo "Content-type: text/html"
echo ""

echo "<html>"
echo "<head>"
echo "<meta charset='ISO-8859-5'>"
echo "<title>PBI Monitor</title>"
echo "</head>"
echo "<body>"

echo "<table border=1>"
n=1
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40; do
	echo "<tr><td><a href=http://172.16.35.1$i>172.16.35.1$i</a></td>"
	curl http://root:12345@172.16.35.1$i/cgi-bin/status.cgi 2> /dev/null | grep -E "&nbsp;IP-1|&nbsp;IP-2|readonly|^&nbsp;2|Service Name:" | while read line ;do
		case $n in 
			[1])
				color1=`echo $line | sed 's/"/ /g' | awk '{print $5}' | sed 's/warning/red/g' | sed 's/ok/#00FF00/g'`
			;;
			[2])
				speed1=`echo $line | awk '{print $5}' | sed 's/value="//g' | sed 's/"//g'`
			;;
			[3])
				ip1=`echo $line | sed 's/&nbsp;//g' | sed 's/<\/td>//g'`
			;;
			[4])
				color2=`echo $line | sed 's/"/ /g' | awk '{print $5}' | sed 's/warning/red/g' | sed 's/ok/#00FF00/g'`
			;;
			[5])
				speed2=`echo $line | awk '{print $5}' | sed 's/value="//g' | sed 's/"//g'`
			;;
			[6])
				ip2=`echo $line | sed 's/&nbsp;//g' | sed 's/<\/td>//g'`
			;;
			[7])
				name1=`echo $line | sed 's/<td>Service Name:&nbsp;//g' | sed 's/<\/td>//g'`
#					name1=`curl http://root:12345@172.16.35.1$i/cgi-bin/decoder2.cgi 2>/dev/null | grep "service_name" | awk '{print $5}' | sed 's/value="//g' | sed 's/"//g'`
			;;
			[8])
				name2=`echo $line | sed 's/<td>Service Name:&nbsp;//g' | sed 's/<\/td>//g'`
				echo "<td bgcolor='$color1'>$ip1</td><td bgcolor='$color1'>$speed1</td><td bgcolor='$color1'>$name1</td>"
				echo "<td bgcolor='$color2'>$ip2</td><td bgcolor='$color2'>$speed2</td><td bgcolor='$color2'>$name2</td>"
			;;
		esac
		n=$(( $n+1 ))
	done
	echo "</tr>"
done
echo "</table></body></html>"
#!/bin/sh

user="user"
password="password"

ONTReboot(){
expect -c "
spawn telnet $1
expect \"Username(1-32 chars):\"
send \"$2\r\"
expect \"Password(1-16 chars):\"
send \"$3\r\"
expect \">\"
send \"enable\r\"
expect \"#\"
send \"configure terminal\r\"
expect \"#\"
send \"ont $4\r\"
expect \"#\"
send \"ont-reboot\r\"
expect \"]\"
send \"y\r\"
expect \"#\"
send \"exit\r\"
expect \"#\"
send \"exit\r\"
expect \"#\"
send \"exit\r\"
expect \">\"
send \"exit\r\"
"
}

#for ip in 106 107 109 110 112 115 119 120 122 126 186 129 189 130 133 183 136 137 138 188 140 152 154 155 158 190 191 192 193 194 195 196 197;do
#    for i in `snmpwalk -On -v2c -c public 172.16.199.$ip .1.3.6.1.4.1.27514.1.11.4.1.1.1 | sed 's/.1.3.6.1.4.1.27514.1.11.4.1.1.1.//g' | awk '{print $1}' | sed 's/\./\//g'`; do
#	ONTReboot 172.16.199.$ip $user $password $i
#    done
#done


echo "Content-type: text/html"
echo ""



echo "<html>"
echo "<head>"
echo "</head>"
echo "<body>"
cat << META
<form>
<select name="num">
    <option value="106">6</option>
    <option value="107">7</option>
    <option value="109">9</option>
    <option value="110">10</option>
    <option value="112">12</option>
    <option value="115">15</option>
    <option value="119">19</option>
    <option value="120">20</option>
    <option value="122">22</option>
    <option value="126">26</option>
    <option value="186">26-2</option>
    <option value="129">29</option>
    <option value="189">29-2</option>
    <option value="130">30</option>
    <option value="133">33</option>
    <option value="183">33-2</option>
    <option value="136">36</option>
    <option value="137">37</option>
    <option value="138">38</option>
    <option value="188">38-2</option>
    <option value="140">40</option>
    <option value="152">52</option>
    <option value="154">54</option>
    <option value="155">55</option>
    <option value="158">58</option>
    <option value="190">90</option>
    <option value="191">91</option>
    <option value="192">92</option>
    <option value="193">93</option>
    <option value="194">94</option>
    <option value="195">95</option>
    <option value="196">96</option>
    <option value="197">97</option>
</select>
<br><input type="submit" value="Перезагрузить">
</form>
META
ip=`env | grep QUERY_STRING | sed 's/QUERY_STRING=//g' | sed 's/num=//g'`
if [ -n "$ip" ]; then
    echo "ip is:"$ip"<br>"
    echo "Strart rebooting all ont on it<br>"
    for i in `snmpwalk -On -v2c -c public 172.16.199.$ip .1.3.6.1.4.1.27514.1.11.4.1.1.1 | sed 's/.1.3.6.1.4.1.27514.1.11.4.1.1.1.//g' | awk '{print $1}' | sed 's/\./\//g'`; do
	echo Reboot $i
	ONTReboot 172.16.199.$ip $user $password $i > /dev/null
	echo "Ok<br>"
    done
fi
echo "</body>"
echo "</html>"
if [ "a$1" = "aall" ]; then
    echo "Rebooting all!"
    for ip in "106 107 109 110 112 115 119 120 122 126 186 129 189 130 133 183 136 137 138 188 140 152 154 155 158 190 191 192 193 194 195 196 197"; do
	echo $ip
	for i in `snmpwalk -On -v2c -c public 172.16.199.$ip .1.3.6.1.4.1.27514.1.11.4.1.1.1 | sed 's/.1.3.6.1.4.1.27514.1.11.4.1.1.1.//g' | awk '{print $1}' | sed 's/\./\//g'`; do
	    echo Reboot $i
	    ONTReboot 172.16.199.$ip $user $password $i > /dev/null
	    echo "Ok<br>"
	done
    done
fi

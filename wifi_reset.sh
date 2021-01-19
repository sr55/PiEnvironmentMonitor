#!/bin/bash

# The Wifi on the Pi Zero appears can drop from time to time.
# This script will reconnect the WIFI should it drop.
# Setup with a contab as root: 
# */5 * * * * /home/pi/wifi_reset.sh >> /home/pi/wifi.log 2>&1

ip="10.0.100.29/24"
wlan_interface="wlan0"
router="10.0.100.1"
google="8.8.8.8"

ping -q -c1 $google > /dev/null
DateTime=$(date)

if [ $? -eq  0 ]
then
    echo "$DateTime - WIFI [OK]"
else   
    echo "$DateTime - WIFI [Offline]"
    echo "- Shutdown wpa_supplicant"
    killall -v wpa_supplicant
    sleep 5
    killall -v wpa_supplicant
    echo "- Bring the interface back up"
    ifconfig $wlan_interface $ip
    ifconfig $wlan_interface up
    sleep 5
    wpa_supplicant -B -c/etc/wpa_supplicant/wpa_supplicant.conf -i$wlan_interface -Dnl80211,wext
    sleep 5
    ip link set $wlan_interface up
    sleep 5
    ROUTE=$(ip route)
    ip route add default via $router dev $wlan_interface
fi

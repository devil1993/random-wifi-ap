import os
import datetime
import time
from subprocess import check_output
import thread

# Time to search for available wifi connections in miliseconds.
time_to_search = 5

# App Constants
disarm_DB_name = "DisarmHotspotDB"
disarm_DB_password = "DisarmDB"

# Wifi Scanning command section
# Find wlan0 and eth0 Interface
wifiInterfaceName = "ls /sys/class/net | grep '^w'"
ethInterfaceName = "ls /sys/class/net | grep '^e'"

wifi_device_name = check_output(wifiInterfaceName, shell=True)[0:-1]
print 'Wifi Interface Name:' + wifi_device_name

eth_device_name = check_output(ethInterfaceName, shell=True)[0:-1]
print 'Ethernet Interface Name:' + eth_device_name

#print 'wifi:' + str(wifi_device_name) + 'eth:' + str(eth_device_name)

command = "iwlist"
operation = "scan"
filters = "| grep -e ESSID -e Quality"
filename = "tempFile1"
to_file = "> " + filename
check_command = "iwconfig"
check_filter = " | grep ESSID"
#to_file = ""

# Wifi Connect Command
connect_to = "nmcli d wifi connect "
disconnect_command = "nmcli d disconnect "
connect_pwd = " password "

# Create AP constants and commands
time_to_wait = 10
sudo_password = "devil.666"
binary_location = "create_ap/create_ap"
create_ap_option = "-g"
ip_range_selector = "192.168.43.1"	
source_device_name = eth_device_name

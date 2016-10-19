import os
import datetime
import time
from subprocess import check_output
import thread
import random

# Time to search for available wifi connections in miliseconds.
time_to_search = 5

# App Constants
disarm_DB_name = "DisarmHotspotDB_testSG"
disarm_DB_password = "DisarmDB"

# Wifi Scanning command section
# Find wlan0 and eth0 Interface
wifiInterfaceName = "ls /sys/class/net | grep w"
ethInterfaceName = "ls /sys/class/net | grep e"

wifi_device_name = check_output(wifiInterfaceName, shell=True)[0:-1]
print wifi_device_name

eth_device_name = check_output(ethInterfaceName, shell=True)[0:-1]
print eth_device_name

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

# AP kill command
kill_ap = "pkill -f create_ap"

# Create AP constants and commands
time_to_wait = 10
sudo_password = "roguenation"
binary_location = "create_ap/create_ap"
create_ap_option = "-g"
ip_range_selector = "192.168.43.1"	
source_device_name = eth_device_name
switching_probability = 0.5

# Functions
def isConnected(connection_name_to_check):
	final_check_command = check_command + " " + wifi_device_name + check_filter
	check_result = check_output(final_check_command, shell=True)
	connected_to = check_result[check_result.find(connection_name_to_check):]
	expected_length = len(connection_name_to_check)
	connected_to = connected_to[:expected_length]
	return connected_to == connection_name_to_check
	
def checkIfDBExists(filename):
	file = open(filename,"r")
	lines = file.read().split('\n')
	name_indicator = 0
	for line in lines:
		line_content = line.strip()
		if(name_indicator == 0):
			name_indicator = 1
		else:
			name_indicator = 0
			connection_name = line_content.split(':')[1]
			connection_name = connection_name[1:-1]
			if(connection_name == disarm_DB_name):
				return 1
			#print connection_name
	return 0

def connectToDB():
	print "Connecting to " + disarm_DB_name	
	final_command = connect_to + disarm_DB_name + connect_pwd + disarm_DB_password
	os.system(final_command)
	#Popen(final_command, shell=True)

def searchAndConnect():
	#datetime.datetime.now().time()
	time_remaining = time_to_search
	current_time = time.time()
	time_taken = 0
	while ((time_remaining - time_taken) > 0 and (not isConnected(disarm_DB_name))):
		try:
			os.system('rm ' + filename)
		except Exception, e:
			print e
		os.system(command + " "	 + wifi_device_name + " " + operation + " " + filters + " " + to_file)
		if(checkIfDBExists(filename) == 1) :
			connectToDB();
		now = time.time()
		#datetime.datetime.now().time()
		time_taken = now - current_time

		#time_remaining = time_remaining - time_taken
		#rint str(time_taken) + " " + str(time_remaining)
		if(time_remaining <= time_taken):
			print "Need to enter randomize switching"
			break;
def randomSwiching():
	frac = random.random()
	if frac > switching_probability:
		return True
	return False

def createAp():
	os.system(disconnect_command+wifi_device_name)
	create_ap_command = binary_location + " " + create_ap_option+ " " + ip_range_selector + " " + wifi_device_name + " " + source_device_name + " " + disarm_DB_name + " " + disarm_DB_password
	print create_ap_command
	# Create AP using the create_ap api
	#p = os.system('echo %s|sudo -S %s' % (sudo_password, create_ap_command))
	thread.start_new_thread( apCreaterThreadFunction, (create_ap_command , 1) )
	# Wait for a constant amount(configured) time
	print "Waiting...."
	time.sleep(time_to_wait)

	# Check if any device is connected with it
	# Loop until - NO DEVICE IS CONNECTED

	# Testing: terminating the ap and killing the creator thread
	os.system(kill_ap)

def apCreaterThreadFunction(command, thread_id):
	#os.popen("sudo -S %s"%(command), 'w').write(sudo_password)
	os.system(command)

# Initially in WiFi mode
#searchAndConnect()
createAp()

# Now loop and randomize switch
while(True):
	break
	# Generate a random fraction
	# Check if its more than switching probability
	if(randomSwiching()):
		createAp()
	else:
		searchAndConnect()

print "Exiting..."
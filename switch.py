import os
import datetime
import time
from subprocess import check_output
import thread
import random
import csv
import logging

# Wifi Scanning command section
# Find wlan0 and eth0 Interface
wifiInterfaceName = "ls /sys/class/net | grep '^w'"
ethInterfaceName = "ls /sys/class/net | grep '^e'"

wifi_device_name = check_output(wifiInterfaceName, shell=True)[0:-1]
print 'Wifi Interface Name:' + wifi_device_name

eth_device_name = check_output(ethInterfaceName, shell=True)[0:-1]
print 'Ethernet Interface Name:' + eth_device_name

# Logger File
logFileName = "PCDisarmConnectLog_" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + ".csv"
# create logger
lgr = logging.getLogger("PCDisarmConnect")
lgr.setLevel(logging.DEBUG) # log all escalated at and above DEBUG
fh = logging.FileHandler(logFileName)
fh.setLevel(logging.DEBUG) # ensure all messages are logged to file
# create a formatter and set the formatter for the handler.
frmt = logging.Formatter('%(asctime)s,%(name)s,%(levelname)s,%(message)s')
fh.setFormatter(frmt)
# add the Handler to the logger
lgr.addHandler(fh)


# Create AP constants and commands
time_to_wait = 30
sudo_password = "roguenation"
binary_location = "create_ap/create_ap"
create_ap_option = "-g"
ip_range_selector = "192.168.43.1"	
source_device_name = eth_device_name
switching_probability = 0.5
activeWifis = []
wifiDict = {}

# Time to search for available wifi connections in miliseconds.
time_to_search = 20

# App Constants
disarm_DB_name = "DisarmHotspotDB"
disarm_DB_password = "DisarmDB"
disarm_device_suffix = "DH-"
disarm_device_password = "password123"

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

# Get the number of connected clients
client_count_script = binary_location + " --list-clients "+ wifi_device_name +" | grep -e 192.168.43 | wc -l"

# AP kill command
kill_ap = "pkill -f create_ap"

# Functions

def isConnected(connection_name_to_check):
	final_check_command = check_command + " " + wifi_device_name + check_filter
	check_result = check_output(final_check_command, shell=True)
	connected_to = check_result[check_result.find(connection_name_to_check):]
	expected_length = len(connection_name_to_check)
	connected_to = connected_to[:expected_length]
	return connected_to == connection_name_to_check
	
def parseWifiList(activeWifiList):
	activeWifis = activeWifiList.replace(" ","").split("\n")

	# Iterate list in increment of two
	for i in xrange(0,len(activeWifis) - 1,2):
		activeWifis[i] = activeWifis[i][25:-3]
		for ch in ['ESSID',':','\"']:
			if ch in activeWifis[i+1]:
				activeWifis[i+1] = activeWifis[i+1].replace(ch,"")

		#print str(activeWifis[i]) + " " + str(activeWifis[i+1])
		wifiDict[activeWifis[i+1]] = int(activeWifis[i])
		 
	lgr.info("Wifi Scan List Result:," + str(wifiDict))
	#print wifiDict
	return wifiDict

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

def connectTo(connection, password):
	print "Connecting to " + connection
	final_command = connect_to + connection + connect_pwd + password
	os.system(final_command)
	#Popen(final_command, shell=True)

def searchAndConnectToDH():
	lgr.info("Searching DisarmDevice")
	#datetime.datetime.now().time()
	time_remaining = time_to_search
	current_time = time.time()
	time_taken = 0
	while ((time_remaining - time_taken) > 0 and (not isConnected(disarm_device_suffix))):
		'''
		try:
			os.system('rm ' + filename)
		except Exception, e:
			print e
		'''
		active_wifi_list = ""
		try:
			active_wifi_list = str(check_output(command + " "	 + wifi_device_name + " " + operation + " " + filters, shell=True))
		except Exception as e:
			lgr.warning(e)
		
		available_connections = parseWifiList(active_wifi_list)
		#print available_connections
		#os.system(command + " "	 + wifi_device_name + " " + operation + " " + filters + " " + to_file)
		best_connection = ''
		best_connection_strength = 0
		for key in available_connections:
			if available_connections[key]<best_connection_strength and key.startswith(disarm_device_suffix):
				best_connection = key
				best_connection_strength = available_connections[key]
		print "Best connection is", best_connection, "with strength = ", best_connection_strength

		if best_connection.startswith(disarm_device_suffix):
			connectTo(best_connection,disarm_device_password);

		now = time.time()
		#datetime.datetime.now().time()
		time_taken = now - current_time

		#time_remaining = time_remaining - time_taken
		#rint str(time_taken) + " " + str(time_remaining)
		if(time_remaining <= time_taken):
			print "Need to enter randomize switching"
			break;

def searchAndConnectToDB():
	lgr.info("Searching DisarmDB")
	#datetime.datetime.now().time()
	time_remaining = time_to_search
	current_time = time.time()
	time_taken = 0
	while ((time_remaining - time_taken) > 0 and (not isConnected(disarm_DB_name))):
		'''
		try:
			os.system('rm ' + filename)
		except Exception, e:
			print e
		'''
		active_wifi_list = ""
		try:
			active_wifi_list = str(check_output(command + " "	 + wifi_device_name + " " + operation + " " + filters, shell=True))
		except Exception as e:
			lgr.warning(e)
		
		available_connections = parseWifiList(active_wifi_list)
		#print available_connections
		#os.system(command + " "	 + wifi_device_name + " " + operation + " " + filters + " " + to_file)
		if available_connections.has_key(disarm_DB_name) :
			connectTo(disarm_DB_name,disarm_DB_password);
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
	print "Random generated number: ", frac
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

	while(True):
		# Wait for a constant amount(configured) time
		print "Waiting...."
		time.sleep(time_to_wait)
		# Check if any device is connected with it
		clients = int(check_output(client_count_script, shell = True))
		if(clients == 0):
			print "No client connected.."
			break
		else:
			print str(clients) + " clients connected."
	
	# Testing: terminating the ap and killing the creator thread
	os.system(kill_ap)

def apCreaterThreadFunction(command, thread_id):
	#os.popen("sudo -S %s"%(command), 'w').write(sudo_password)
	os.system(command)

# Initially in WiFi mode

searchAndConnectToDB()
#createAp()

# Now loop and randomize switch
while(True):
	print "Sleeping for 5 secs"
	time.sleep(5)
	print "Good morning, again!!"
	# Check if connected to any device or DB
	while(isConnected(disarm_device_suffix) or isConnected(disarm_DB_name)):
		print "Waiting for connections to get terminated.."
		time.sleep(time_to_wait)
	# Generate a random fraction
	# Check if its more than switching probability
	if(randomSwiching()):
		print "Creating AP......"		
		createAp()
	else:
		print "Searching for devices........"
		searchAndConnectToDH()

print "Exiting..."

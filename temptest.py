import usb.core
import usb.util
import serial
import time 
import os
import glob


# Global settings
DESCRIPTION = "5 days at 60s interval testing 1.5V Energizer with 0.33ohm load drawing constant 100mA"
#DESCRIPTION = "5 days temperature test at 10 minute intervals"
DAYS = 5
DURATION = 86400 * DAYS		#Run duration in seconds.
PERIOD = 60 			#Sampling period in seconds
TIMEOUT = 1
FILENAME = "/home/pi/Desktop/myPython/Batt31Jul1.txt"
MOUNTPOINT = "/dev/ttyUSB0"
GPIBADDR = "++addr 8"
COMMAND = "*IDN?"


# Set up the USB port with the GPIB card
port =serial.Serial(
    MOUNTPOINT,
    baudrate=460800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    writeTimeout = 0,
    timeout = TIMEOUT,
    rtscts=False,
    dsrdtr=False,
    xonxoff=False)

# Set up the thermometer
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Function to read the low level thermometer data
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
# Function to turn thermometer data into something useful
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        #return temp_c, temp_f
	return temp_c
	
# Write to the GPIB card
def writeUSB(writeOut):
	port.write(writeOut+"\r")
	
# Read from GPIB
def readUSB():
	while True:
    		response=port.readlines()
    		break
	readIn = ''.join(response)
	return readIn

# Save data to flash disk by appending to file
def writeFile(data):
	with open(FILENAME, 'a') as f:
    		f.write(data+"\n")

# Clear old results file if present
try:
	os.remove(FILENAME)
except OSError:
	pass

# Get run time
def getRunTime():
	localtime = time.asctime( time.localtime(time.time()) )
	print "Local current time :", localtime
	writeFile(DESCRIPTION)
	writeFile(localtime)

# GPIB set up
def startGPIB():
	print("Looking for GPIB and testing link...")
	writeUSB("+test")
	print(readUSB())

	writeUSB("++ver")
	print(readUSB())

	print("Setting GPIB address\n")
	writeUSB(GPIBADDR)




# Runtime starts here
startGPIB()

timeStart = time.time()
timeEnd = timeStart + DURATION
writeFile(DESCRIPTION)
writeFile ("Start Time: " + str(timeStart))
writeFile("End Time: " + str(timeEnd))

print ("Running ....")
sample=0

#Loop and read voltage, time and temperature
while time.time() < timeEnd:
	sample=sample+1
	writeUSB(COMMAND)
	timeNow=time.strftime("%m/%d/%y %H:%M:%S",time.localtime())
	data=readUSB()
	data=data.rstrip()
	temp=read_temp()
	writeFile(str(sample) + "," + timeNow + ","+ str(temp) + "," + str(data))
#	writeFile(str(sample) + "," + timeNow + ","+ str(temp))
	print ("Sample: "+str(sample))
	time.sleep(PERIOD)

print ("\n")
print ("Ends...")
 
 


#!/usr/bin/python

# program data.py 

# vIbscope

import smbus
from datetime import datetime, timedelta
import time

bus = smbus.SMBus(1) # Bus for Revision 2 boards
address = 0x68       # Sensor i2c address
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

# Accelerometer
# Data register
ACCEL_XOUT0 = 0x3B
ACCEL_XOUT1 = 0x3C
ACCEL_YOUT0 = 0x3D
ACCEL_YOUT1 = 0x3E
ACCEL_ZOUT0 = 0x3F
ACCEL_ZOUT1 = 0x40
# Range
ACCEL_CONFIG_REGISTER = 0x1C
ACCEL_2G = 0x00
ACCEL_4G = 0x08
ACCEL_8G = 0x10
ACCEL_16G = 0x18
# Scale Modifiers
ACCEL_SCALE_MODIFIER_2G = 16384.0
ACCEL_SCALE_MODIFIER_4G = 8192.0
ACCEL_SCALE_MODIFIER_8G = 4096.0
ACCEL_SCALE_MODIFIER_16G = 2048.0

# Gyroscope
# Data register
GYRO_XOUT0 = 0x43
GYRO_XOUT1 = 0x44
GYRO_YOUT0 = 0x45
GYRO_YOUT1 = 0x46
GYRO_ZOUT0 = 0x47
GYRO_ZOUT1 = 0x48
# Range
GYRO_CONFIG_REGISTER = 0x1B
GYRO_250DEG = 0x00
GYRO_500DEG = 0x08
GYRO_1000DEG = 0x10
GYRO_2000DEG = 0x18
# Scale Modifiers
GYRO_SCALE_MODIFIER_250DEG = 131.0
GYRO_SCALE_MODIFIER_500DEG = 65.5
GYRO_SCALE_MODIFIER_1000DEG = 32.8
GYRO_SCALE_MODIFIER_2000DEG = 16.4

# Temperature
# Data register
TEMP_OUT0 = 0x41
TEMP_OUT1 = 0x42

# -- Functions --
def read_register(adr):
    return [bus.read_byte_data(address, adr),bus.read_byte_data(address, adr+1)]

def convert_register(raw_val):
    convert_val = (raw_val[0] << 8) + raw_val[1]
    if (convert_val >= 0x8000):
        return -((65535 - convert_val) + 1)
    else:
        return convert_val

def convert_temp(raw_val):
    raw_temp = convert_register(raw_val)
    temp = (raw_temp / 340) + 36.53
    return temp

def set_range_get_scale(register, range):
    bus.write_byte_data(address, register, range) # set new range
    time.sleep(0.5)
    current_range = bus.read_byte_data(address, register) # read current set range
    if register == ACCEL_CONFIG_REGISTER:
        if current_range == ACCEL_2G:
            return ACCEL_SCALE_MODIFIER_2G
        elif current_range == ACCEL_4G:
            return ACCEL_SCALE_MODIFIER_4G
        elif current_range == ACCEL_8G:
            return ACCEL_SCALE_MODIFIER_8G
        else: #current_range == ACCEL_16G
            return ACCEL_SCALE_MODIFIER_16G
    if register == GYRO_CONFIG_REGISTER:
        if current_range == GYRO_250DEG:
            return GYRO_SCALE_MODIFIER_250DEG
        elif current_range == GYRO_500DEG:
            return GYRO_SCALE_MODIFIER_500DEG
        elif current_range == GYRO_1000DEG:
            return GYRO_SCALE_MODIFIER_1000DEG
        else: #current_range == GYRO_2000DEG:
            return GYRO_SCALE_MODIFIER_2000DEG  
 
# -- INIT -- 
print('| Loading...')
bus.write_byte_data(address, power_mgmt_1, 0)
acc_scale = set_range_get_scale(ACCEL_CONFIG_REGISTER,ACCEL_2G)
gyro_scale = set_range_get_scale(GYRO_CONFIG_REGISTER,GYRO_250DEG)

# -- MAIN --
# query of parameters
freqInput = raw_input("Measuring frequency[Hz]: ")
durationInput=[0,0]
tmp = raw_input("Measuring duration[m]: ")
durationInput[0] = int(tmp)
tmp = raw_input("Measuring duration[s]: ")
durationInput[1] = int(tmp)

# Calculation of frequency
milsec = float(1000.0/float(freqInput))
if milsec==1000:
   freq=timedelta(0,1)
elif milsec%1==0:
   freq=timedelta(0,0,0,int(milsec))
else:
   freq=timedelta(0,0,(milsec-int(milsec))*1000,int(milsec))

# Set measurement duration
duration=timedelta(0,durationInput[1],0,0,durationInput[0]) # days, seconds, microseconds, milliseconds, minutes

# List for data record
time=[]
temp=[]
acc=[]
gyro=[]

# Loop
print('| Start Logging')
tend = datetime.now()+duration
t = datetime.now()
while datetime.now().time() < tend.time(): # interrupts if the total measuring time is passed
    t = datetime.now()
    time.append(datetime.now())
    temp.append(read_register(0x41))
    acc.append([read_register(0x3B),read_register(0x3D),read_register(0x3F)])
    gyro.append([read_register(0x43),read_register(0x45),read_register(0x47)])
    while datetime.now() < t+freq:  # interrupts if it time for the next record
        pass
tend = datetime.now()
print('| Finish Logging')

# Test Records
print('| Start Test Record')
if len(time) == len(temp) and len(time) == len(acc) and len(time) == len(gyro):
    print('| Finish Record Test; Result = OK')
else:
    print('| Finish Record Test; Result = FALSE')
    SystemExit(0)

# Convert Raw Data
print('| Start Raw Data Converting')
for i in range(len(time)):
    temp[i] = convert_temp(temp[i])
    for j in range(0,3):
        acc[i][j] = convert_register(acc[i][j]) / acc_scale
        gyro[i][j] = convert_register(gyro[i][j]) / gyro_scale
print('| Finish Raw Data Converting')

# write file
print ("| Start file writing")
name = datetime.now()
file = name.strftime('%Y%m%d_%H%M%S')
datei_out = open(file+".csv","w")
for i in range(len(time)):
    datei_out.write(str(i+1)+";") # number of measurment
    datei_out.write(str(time[i].time())+";") # time stamp of measurment
    datei_out.write(str(time[i]-time[0])+";") # time delta since measurement start
    datei_out.write(str(acc[i][0])+";") # Accelerometer X
    datei_out.write(str(acc[i][1])+";") # Accelerometer X
    datei_out.write(str(acc[i][2])+";") # Accelerometer X
    datei_out.write(str(gyro[i][0])+";") # Gyroscope X
    datei_out.write(str(gyro[i][1])+";") # Gyroscope X
    datei_out.write(str(gyro[i][2])+"\n") # Gyroscope X
datei_out.close()
print ("| Finish file writing")

# end
print ("| Completely Finish")

#!/usr/bin/env python3    ¡¡¡ OK !!!
# Program MPU.py
# - Corrected g_scale.
# - g_scale = (Vref / ADC resolution) * (300 mv/g)
# - Error noted and corrected by Steve Ferry.
# 08/02/2019
# - Added a timeout control to a while loop.
# 12/02/2019
# Program fft_spectrum_gui_3can.py modified:
# - From Python 2.7 to Python 3.5.
# - Works with plot.py
# 20/02/2019
# Program fft_spectrum_gui_3can.py
# Program fft_spectrum_gui.py modified:
# - 3 data channels (3 axes)
# 1/03/2019
# Program fft_spectrum_gui.py 
# - Based on program frame_tab_plot_07.py
# - Sample acceleration data from a MPU6050 accelerometer.
# - Plot sampled data and its FFT spectrum
# - Save data on file and open files with saved data.
# - I2C communication with microcontroller.e
# - I2C bus selection.
# - RadioButtons to select a Window function to apply.
# 02/03/2019

# vIbscope


import smbus
import time as time
import math as math
import csv
import datetime
from scipy import fftpack
import numpy as np

class mpu6050:

    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = smbus.SMBus(1)

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    def __init__(self, address):
        self.address = address

        # Wake up the MPU-6050 since it starts in sleep mode
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)

    # I2C communication methods

    def read_i2c_word(self, register):
        """Read two i2c registers and combine them.

        register -- the first register to read from.
        Returns the combined read results.
        """
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # MPU-6050 Methods

    def get_temp(self):
        """Reads the temperature from the onboard temperature sensor of the MPU-6050.

        Returns the temperature in degrees Celcius.
        """
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)

        # Get the actual temperature using the formule given in the
        # MPU-6050 Register Map and Descriptions revision 4.2, page 30
        actual_temp = (raw_temp / 340.0) + 36.53

        return actual_temp

    def set_accel_range(self, accel_range):
        """Sets the range of the accelerometer to range.

        accel_range -- the range to set the accelerometer to. Using a
        pre-defined range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)

    def read_accel_range(self, raw = False):
        """Reads the range the accelerometer is set to.

        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g = False):
        """Gets and returns the X, Y and Z values from the accelerometer.

        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accel_scale_modifier = None
        accel_range = self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_8G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range - accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G")
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_gyro_range(self, gyro_range):
        """Sets the range of the gyroscope to range.

        gyro_range -- the range to set the gyroscope to. Using a pre-defined
        range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_range)

    def read_gyro_range(self, raw = False):
        """Reads the range the gyroscope is set to.

        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        """
        raw_data = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self):
        """Gets and returns the X, Y and Z values from the gyroscope.

        Returns the read values in a dictionary.
        """
        x = self.read_i2c_word(self.GYRO_XOUT0)
        y = self.read_i2c_word(self.GYRO_YOUT0)
        z = self.read_i2c_word(self.GYRO_ZOUT0)

        gyro_scale_modifier = None
        gyro_range = self.read_gyro_range(True)

        if gyro_range == self.GYRO_RANGE_250DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG
        elif gyro_range == self.GYRO_RANGE_500DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_500DEG
        elif gyro_range == self.GYRO_RANGE_1000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_1000DEG
        elif gyro_range == self.GYRO_RANGE_2000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("Unkown range - gyro_scale_modifier set to self.GYRO_SCALE_MODIFIER_250DEG")
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG

        x = x / gyro_scale_modifier
        y = y / gyro_scale_modifier
        z = z / gyro_scale_modifier

        return {'x': x, 'y': y, 'z': z}

    def get_all_data(self):
        """Reads and returns all the available data."""
        temp = self.get_temp()
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()

        return [accel, gyro, temp]

def complementray_filter(one_gyro_angle, one_accel_angle, alpha=0.96):
    """ docstring """
    #http://www.geekmomprojects.com/gyroscopes-and-accelerometers-on-a-chip/
    return alpha*one_gyro_angle + (1.0 - alpha)*one_accel_angle

def get_base_value():
    """ docstring """
    for idx in range(0, 9):
        accel_data = mpu.get_accel_data()
        gyro_data = mpu.get_gyro_data()

        sumAc = {'x':0,'y':0,'z':0}
        sumGy = {'x':0,'y':0,'z':0}

        sumAc['x'] += accel_data['x']
        sumAc['y'] += accel_data['y']
        sumAc['z'] += accel_data['z']
        sumGy['x'] += gyro_data['x']
        sumGy['y'] += gyro_data['y']
        sumGy['z'] += gyro_data['z']

        time.sleep(0.1)
  
    baseAc['x'] = sumAc['x'] / 10
    baseAc['y'] = sumAc['y'] / 10
    baseAc['z'] = sumAc['z'] / 10
    baseGy['x'] = sumGy['x'] / 10
    baseGy['y'] = sumGy['y'] / 10
    baseGy['z'] = sumGy['z'] / 10

    return baseAc, baseGy

def get_angle(side, side2, z):
    """ docstring """
    RADIANS_TO_DEGREES = 180 / 3.141592
    sideZ = math.sqrt(math.pow(side, 2) + pow(z, 2))
    return math.atan(side2 / sideZ) * RADIANS_TO_DEGREES

def get_value_with_out_base_value(data, base):
    """ docstring """
    data['x'] = data['x'] - base['x']
    data['y'] = data['y'] - base['y']
    data['z'] = data['z'] - base['z'] + 16384
    return data


#other constants
samples_to_read = 10000
sample_rate = 1030

channel_1 = []
channel_2 = []
channel_3 = []


def conv_str_tag(channel, tag):
    # Convert every channel from int to str, separated by a coma and adds tags at the beginning and end.
    n = len(channel)
    s_channel = '<' + tag + '>'
    for i in range(n-1):
        s_channel = s_channel + str(channel[i]) + ','
    s_channel = s_channel + str(channel[n-1]) + '</'+ tag + '>'
    return s_channel

#####Add tags and save on file#####
def record(channel_1, channel_2, channel_3, archive):
    str_channel = ''
    str_channel += conv_str_tag(channel_1, 'L1') + '\n'
    str_channel += conv_str_tag(channel_2, 'L2') + '\n'
    str_channel += conv_str_tag(channel_3, 'L3') + '\n'

    # Write to file
    arch = open("/home/pi/Desktop/vibration-analysis"+archive, "w")
    arch.write(str_channel)
    arch.close()

def mainprog():    
    mpu = mpu6050(0x68)
    print("START")
    print("Collecting sensor readings")
    sample_counter = 0;
    while(sample_counter < samples_to_read):
        axes = mpu.get_accel_data()    
        #put the axes into variables
        x = axes['x']
        y = axes['y']
        z = axes['z']
    	
        channel_1.append(x)
        channel_2.append(y)
        channel_3.append(z)
    	
        sample_counter = sample_counter + 1;
    #end of while loop
    
    print("Amount of samples in channel 1: %s" %len(channel_1))
    print("Amount of samples in channel 2: %s" %len(channel_2))
    print("Amount of samples in channel 3: %s" %len(channel_3))
    
    #####saving to TXT file#####
    archive = "textfile_"
    archive += datetime.datetime.now().strftime("%d-%m-%Y__%H_%M_%S")
    archive += ".txt"
    print("Saving to %s" %archive)
    record(channel_1, channel_2, channel_3, archive)
    
    #####Calculate average value for each channel#####
    num_data = len(channel_1)
    X = range(0, num_data, 1)
    vdc_channel_1 = 0
    vdc_channel_2 = 0
    vdc_channel_3 = 0
    for indice in X:
        vdc_channel_1 += channel_1[indice]
        vdc_channel_2 += channel_2[indice]
        vdc_channel_3 += channel_3[indice]
    vdc_channel_1 = vdc_channel_1 / num_data
    vdc_channel_2 = vdc_channel_2 / num_data
    vdc_channel_3 = vdc_channel_3 / num_data
    
    print"Vdc Channel 1: ",vdc_channel_1
    print"Vdc Channel 2: ",vdc_channel_2
    print"Vdc Channel 3: ",vdc_channel_3
    
    #####Subtract DC offset#####
    for indice in X:
        channel_1[indice] -= vdc_channel_1
        channel_2[indice] -= vdc_channel_2
        channel_3[indice] -= vdc_channel_3
    
    #####saving to CSV file#####
    archive = "time_logfile_"
    archive += datetime.datetime.now().strftime("%d-%m-%Y__%H_%M_%S")
    archive += ".csv"
    print("Saving to %s" %archive)
    arch = open(archive, "w")
    num_data = len(channel_1)
    indice = 0;
    while (indice < num_data):
        arch.write(str(channel_1[indice])+","+str(channel_2[indice])+","+str(channel_3[indice])+"\n")
        indice = indice+1;
    
    arch.close()
    tname = archive
    print("Saving complete")
    
    #####calculation of fft#####
    
    channel_fft_x = []
    channel_fft_y = []
    channel_fft_z = []
    
    N = len(channel_1) # length of the signal
    T = 1.0 / sample_rate
    xf = np.linspace(0.0, 1.0/(2.0*T), N/2)
    
    yf1 = fftpack.fft(channel_1)
    channel_fft_x = 2.0/N * np.abs(yf1[:N/2])
    
    yf2 = fftpack.fft(channel_2)
    channel_fft_y = 2.0/N * np.abs(yf2[:N/2])
    
    yf3 = fftpack.fft(channel_3)
    channel_fft_z = 2.0/N * np.abs(yf3[:N/2])
    
    #####saving to CSV file#####
    archive = "fft_logfile_"
    archive += datetime.datetime.now().strftime("%d-%m-%Y__%H_%M_%S")
    archive += ".csv"
    print("Saving to %s" %archive)
    arch = open(archive, "w")
    num_data = len(xf)
    indice = 0;
    while (indice < num_data):
        arch.write(str(xf[indice])+","+str(channel_fft_x[indice])+","+str(channel_fft_y[indice])+","+str(channel_fft_z[indice])+"\n")
        indice = indice+1;
        
    arch.close()
    fname = archive
    print("Saving complete")
    return(tname,fname)
    print("END")


if __name__ == "__main__":
    mainprog()

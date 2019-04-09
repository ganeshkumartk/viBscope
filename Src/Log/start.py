"""This program is based on MPU6050
Vibscope
"""
import smbus
import time as time
import math as math
import csv

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

if __name__ == "__main__":
    mpu = mpu6050(0x68)

    mpu.set_accel_range(16)

    Range = mpu.read_accel_range()

    print("Accel Range is " + str(Range) + ".") 
    temp_time = time.time()
    fileName = 'data_'+ str(temp_time) + '.csv' 
    with open(fileName,'w') as f:
        fieldnames = ['Time', 'Acc_x', 'Acc_y', 'Acc_z']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        while 1:
            mpu = mpu6050(0x68)
            print(mpu.get_temp())
            accel_data = mpu.get_accel_data()
            print("Accel")
            print(str(accel_data['x']) + "\t" + str(accel_data['y']) + "\t" + str(accel_data['z']))
            gyro_data = mpu.get_gyro_data()
            print("Gyro")
            print(str(gyro_data['x']) + "\t" + str(gyro_data['y']) + "\t" + str(gyro_data['z']))
            writer.writerow({'Time' : time.time()-temp_time, 'Acc_x' : accel_data['x'], 'Acc_y' : accel_data['y'], 'Acc_z' : accel_data['z']})
            time.sleep(0.1)

        #writer.close()
    """ test 1 """
    """
    baseAc, baseGy = get_base_value()

    while 1:
        accel_data = mpu.get_accel_data()
        gyro_data = mpu.get_gyro_data()
        accel_data = get_value_with_out_base_value(accel_data, baseAc)
        gyro_data = get_value_with_out_base_value(accel_data, baseGy)

        accel_angle = {'x':0, 'y':0, 'z':0}
        gyro_angle = {'x':0, 'y':0, 'z':0}
        angle = {'x':0, 'y':0, 'z':0}

        accel_angle['x'] = get_angle(accel_data['x'], accel_data['y'], accel_data['z'])
        accel_angle['y'] = get_angle(accel_data['y'], accel_data['x'], accel_data['z'])
        #Accelerometer doesn't give z-angle 
        accel_angle['z']= 0 

        accel_angle = get_value_with_out_base_value(accel_angle, baseAc)
        gyro_angle = get_value_with_out_base_value(gyro_data, baseGy)

        
        angle['x'] = complementray_filter(gyro_angle['x'], accel_angle['x'])
        angle['y'] = complementray_filter(gyro_angle['y'], accel_angle['y'])
        angle['z'] = complementray_filter(gyro_angle['z'], accel_angle['z'])

        print("Angle x : " + str(angle['x']))
        print("Angle y : " + str(angle['y']))
        print("Angle z : " + str(angle['z']))
    """
""" test 2 """
"""
compAngleX=0
compAngleY=0
timer = time.micros

while 1:

  accXangle = (atan2(accel_data['y'], accel_data['z']) + PI) * RAD_TO_DEG
  accYangle = (atan2(accel_data['x'], accel_data['z']) + PI) * RAD_TO_DEG

  gyroXrate = (double)gyroX / 131.0
  gyroYrate = -((double)gyroY / 131.0)

  compAngleX = (Alpha * (compAngleX + (gyroXrate * (micros() - timer) / 1000000))) + (1-Alpha * accXangle)
  compAngleY = (Alpha * (compAngleY + (gyroYrate * (micros() - timer) / 1000000))) + (1-Alpha * accYangle)

  timer = micros()

  print("Angle X : " +  str(compAngleX))
  print("Angle Y : " +  str(compAngleY))
"""

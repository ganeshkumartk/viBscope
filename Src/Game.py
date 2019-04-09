import pygame, sys
from pygame.locals import *
import smbus
import math
import time  
pygame.init()
  
# set up the graphics window
WINDOW = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('MPU_6050 ')
  
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
  
# draw on the surface object
WINDOW.fill(WHITE)
#==================================
# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
 
gyro_scale = 131.0
accel_scale = 16384.0
 
address = 0x68  # This is the default I2C address of ITG-MPU breakout board

def read_all():
    raw_gyro_data = bus.read_i2c_block_data(address, 0x43, 6)
    raw_accel_data = bus.read_i2c_block_data(address, 0x3b, 6)

    gyro_scaled_x = twos_compliment((raw_gyro_data[0] << 8) + raw_gyro_data[1]) / gyro_scale
    gyro_scaled_y = twos_compliment((raw_gyro_data[2] << 8) + raw_gyro_data[3]) / gyro_scale
    gyro_scaled_z = twos_compliment((raw_gyro_data[4] << 8) + raw_gyro_data[5]) / gyro_scale
 
    accel_scaled_x = twos_compliment((raw_accel_data[0] << 8) + raw_accel_data[1]) / accel_scale
    accel_scaled_y = twos_compliment((raw_accel_data[2] << 8) + raw_accel_data[3]) / accel_scale
    accel_scaled_z = twos_compliment((raw_accel_data[4] << 8) + raw_accel_data[5]) / accel_scale
    
    return(gyro_scaled_x,gyro_scaled_y,gyro_scaled_z,accel_scaled_x,accel_scaled_y,accel_scaled_z)
#==========================================================
def twos_compliment(val):
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def dist(a, b):
    return math.sqrt((a * a) + (b * b))


bus = smbus.SMBus(1)  # SMBus(1) for Raspberry pi 2 board

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

now = time.time()
 
K = 0.98
K1 = 1 - K
time_diff = 0.01
(gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z) = read_all()

last_x = get_x_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
last_y = get_y_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)

gyro_offset_x = gyro_scaled_x
gyro_offset_y = gyro_scaled_y

gyro_total_x = (last_x) - gyro_offset_x
gyro_total_y = (last_y) - gyro_offset_y
#========================

# run the loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    time.sleep(time_diff - 0.005)
    (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z) = read_all()
    
    gyro_scaled_x -= gyro_offset_x
    gyro_scaled_y -= gyro_offset_y
     
    gyro_x_delta = (gyro_scaled_x * time_diff)
    gyro_y_delta = (gyro_scaled_y * time_diff)

    gyro_total_x += gyro_x_delta
    gyro_total_y += gyro_y_delta

    rotation_x = get_x_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
    rotation_y = get_y_rotation(accel_scaled_x, accel_scaled_y, accel_scaled_z)
 
    last_x = K * (last_x + gyro_x_delta) + (K1 * rotation_x)
    last_y = K * (last_y + gyro_y_delta) + (K1 * rotation_y)
    
    #print last_x,last_y on terminal window
    print (last_x), (last_y)
    
    delta_y = math.radians(last_y)
 
    #z-is thickness of the line
    z = 2 * int(last_x)
    if z < 0 :
        z = -z 
	COLOR = RED
    else:
	COLOR = BLUE
    if z == 0 :
	z = 1

    x1 = 200 -(100 * math.cos(delta_y))
    y1 = 150 +(100 * math.sin(delta_y))	
    x2 = 200 +(100 * math.cos(delta_y))
    y2 = 150 -(100 * math.sin(delta_y))
    
    #print (x1), (y1) ,(x2), (y2)
    WINDOW.fill(WHITE) #clear window before redraw

    #simply draw the plane, z-is thickness: change thickness of the line to appear 3D
    pygame.draw.line(WINDOW, COLOR, (x1,y1), (x2,y2), z) 
    pygame.display.update()

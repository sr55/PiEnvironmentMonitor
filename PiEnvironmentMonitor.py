#!/usr/bin/env python3
import bme680
import time
from time import sleep
import mysql.connector
from datetime import datetime
from ltr559 import LTR559
from picamera import PiCamera

## Dependencies
#  pip3 install bme680
#  pip3 install mysql-connector-python
#  pip3 install smbus
#  pip3 install veml6075
#  pip3 install ltr559
#  pip3 install picamera

# ------------------------------------------------------------
# Config 
# ------------------------------------------------------------
room =  "Loft" # A description of where the sensor is placed.
polling_interval = 15  # Polling interval in seconds.
temp_offset = -2.4  # For calibrating the BME680
ltr559_enabled = False # Enable the light sensor
camera_enabled = False # Will take a picture every interval.

db_enabled = True # Enable database writes.
db_host = "10.0.100.10"
db_user = ""
db_pwd = ""
db_schema = "enviro"
db_port = 3306


# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------
def connectToMySQL():
    try:
        global dbConn 
        dbConn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, db=db_schema, port=db_port)
        global dbCur 
        dbCur = dbConn.cursor()
        return True;
    except Exception as e: 
        print(" - Unable to Connect to MySQL. Check connection Details!")
        print(e)
        print()
        return False;

# ------------------------------------------------------------

# Startup

print('Environment Monitor for Pi 1.0')

# Database Connection
if db_enabled:
    isConnected = connectToMySQL();
    if isConnected:
        print('\n - MySQl Connection [OK] ')
    else:
        print('\n - MySQl Connection [FAILED] ')
        exit()
else:
    print('\n - MySQl Connection [Disabled] ')

# Try to connect to the Sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
except Exception as e: 
    print("Unable to Connect BME680 sensor. Check it's connected!")
    print(e)
    exit()
    
print(' - BME680 Sensor [OK] ')


# Setup for Environment Monitoring 
sensor.set_temp_offset(temp_offset)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_4X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)  # DISABLE_GAS_MEAS 
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# LTR559
if ltr559_enabled:
    ltr559 = LTR559()
    print(' - LTR559 Sensor [OK] ')
    
# Camera
if camera_enabled:
    camera = PiCamera()
    camera.resolution = (1920, 1080)
    print(' - Camera [OK]')

print(' - Polling Interval: {0}'.format(polling_interval))
   
# Start Logging environment data
print('\n\nSensor Data: \n')
try:
    while True:
        now = datetime.now()
        dateTime = now.strftime('%Y-%m-%d %H:%M:%S')
        dateTimeHuman = now.strftime('%d/%m/%Y %H:%M:%S')
        
        if camera_enabled:
            camera.start_preview()
            sleep(2)
            camera.capture('/home/pi/images/' +dateTime+'.jpg')
            camera.stop_preview()
        
        lux = 0;
        if ltr559_enabled:
            ltr559.update_sensor()
            lux = ltr559.get_lux()
       
        if sensor.get_sensor_data():
            output = '{0},     {1:.2f} C,     {2:.2f} hPa,     {3:.2f} %RH    {4:06.2f} Lux'.format(dateTimeHuman, sensor.data.temperature, sensor.data.pressure, sensor.data.humidity, lux)

            if sensor.data.heat_stable:
                print('{0},     {1:.0f} AQ Ohms'.format(output, sensor.data.gas_resistance))
                sql = "INSERT INTO environment_data (room, datetime, temp, pressure, humidity, air_quality, light) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                query_data = (room, dateTime, sensor.data.temperature, sensor.data.pressure, sensor.data.humidity, sensor.data.gas_resistance, lux)
            else:
                sql = "INSERT INTO environment_data (room, datetime, temp, pressure, humidity, light) VALUES (%s, %s, %s, %s, %s, %s)"
                query_data = (room, dateTime, sensor.data.temperature, sensor.data.pressure, sensor.data.humidity, lux)
                print(output)
        
        
            try:
                if db_enabled:
                    dbCur.execute(sql, query_data)
                    dbConn.commit()
            except Exception as e: 
                print(e)
                connectToMySQL();
           

        time.sleep(polling_interval) 

except KeyboardInterrupt:
    pass
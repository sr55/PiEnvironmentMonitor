#!/usr/bin/env python
import bme680
import time
import mysql.connector
from datetime import datetime

## Dependencies
#  pip3 install bme680
#  pip3 install mysql-connector-python
#  pip3 install smbus

# ------------------------------------------------------------
# Config 
# ------------------------------------------------------------
room =  "Office" # A description of where the sensor is placed.
polling_interval = 10  # Polling interval in seconds.
temp_offset = -2.5  # For calibrating the BME680

db_enabled = False # Enables database writes.
db_host = ""
db_user = ""
db_pwd = ""
db_schema = ""
db_port = 3306

# ------------------------------------------------------------

# Startup

print('Environment Monitor for Pi 1.0')

# Database Connection
if db_enabled:
    try:
        dbConn = mysql.connector.connect(host=db_host, user=db_user, passwd=db_pwd, db=db_schema, port=db_port)
        dbCur = dbConn.cursor()
    except Exception as e: 
        print("Unable to Connect to MySQL. Check connection Details!")
        print(e)
        exit()
    print('\n - MySQl Connection [OK] ')
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
print(' - Polling Interval: {0}'.format(polling_interval))

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

# Start Logging environment data
print('\n\nSensor Data: \n')
try:
    while True:
        now = datetime.now()
        dateTime = now.strftime('%Y-%m-%d %H:%M:%S')
        dateTimeHuman = now.strftime('%d/%m/%Y %H:%M:%S')

        if sensor.get_sensor_data():
            output = '{0},     {1:.2f} C,     {2:.2f} hPa,     {3:.2f} %RH'.format(dateTimeHuman, sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)

            if sensor.data.heat_stable:
                print('{0},     {1:.0f} AQ Ohms'.format(output, sensor.data.gas_resistance))
                sql = "INSERT INTO environment_data (room, datetime, temp, pressure, humidity, air_quality) VALUES (%s, %s, %s, %s, %s, %s)"
                query_data = (room, dateTime, sensor.data.temperature, sensor.data.pressure, sensor.data.humidity, sensor.data.gas_resistance)
            else:
                sql = "INSERT INTO environment_data (room, datetime, temp, pressure, humidity) VALUES (%s, %s, %s, %s, %s)"
                query_data = (room, dateTime, sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)
                print(output)
            
            if db_enabled:
                dbCur.execute(sql, query_data)
                dbConn.commit()

        time.sleep(polling_interval) 

except KeyboardInterrupt:
    pass

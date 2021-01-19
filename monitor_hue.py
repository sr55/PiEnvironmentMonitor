#!/usr/bin/env python3
import time
from time import sleep
import mysql.connector
from datetime import datetime
import requests
import json

## Dependencies
#  pip3 install mysql-connector-python
#  pip3 install requests

# ------------------------------------------------------------
# Config 
# ------------------------------------------------------------
bridge_username = ""
bridge_ip = ""

polling_interval = 30

room_temperatures = {
  "Lounge": 13,
  "Upper Hall": 56,
  "Back Bedroom": 62,
}

room_lux = {
  "Lounge": 15,
  "Upper Hall": 58,
  "Back Bedroom": 61,
}

calibration = 0.5;

db_enabled = True # Enable database writes.
db_host = ""
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

def get_hue_sensor_temp(id):
  try:
    response = requests.get('http://' + bridge_ip + '/api/' + bridge_username + '/sensors/' +  str(id))
    json_data = json.loads(response.text)
    return json_data['state']['temperature']
  except Exception as e: 
    print(" - Unable to Connect to Hue.")
    print(e)
    print()
    return None

def get_hue_sensor_light(id):
  try:
    response = requests.get('http://' + bridge_ip + '/api/' + bridge_username + '/sensors/' +  str(id))
    json_data = json.loads(response.text)
    return json_data['state']['lightlevel']
  except Exception as e: 
    print(" - Unable to Connect to Hue. ")
    print(e)
    print()
    return None

# ------------------------------------------------------------

# Startup

print('Hue Monitor for Pi 1.0')

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


print(' - Polling Interval: {0}'.format(polling_interval))
   
# Start Logging environment data
print('\n\nSensor Data: \n')
try:
    while True:
        now = datetime.now()
        dateTime = now.strftime('%Y-%m-%d %H:%M:%S')
        dateTimeHuman = now.strftime('%d/%m/%Y %H:%M:%S')
        
        print(" - " + dateTimeHuman)
        for key in room_temperatures:
            room = key
            temperature = get_hue_sensor_temp(room_temperatures[key]) / 100  +  calibration # Lounge
            lightlevel = get_hue_sensor_light(room_lux[key])

            print("   "+ key +":       " + str(temperature) + "C,   " + str(lightlevel) + " Lux")
           
            if temperature == None or lightlevel == None:
                print ("Skipping due to bad data ...")
                continue;
           
            try:
                if db_enabled:
                    sql = "INSERT INTO environment_data (room, datetime, temp, light) VALUES (%s, %s, %s, %s)"
                    query_data = (room, dateTime, temperature,  lightlevel);
                    dbCur.execute(sql, query_data)
                    dbConn.commit()
            except Exception as e: 
                print(e)
                connectToMySQL();
        
        print()
        time.sleep(polling_interval) 

except KeyboardInterrupt:
    pass
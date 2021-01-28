# Pi Environment Monitor
Collection of Python scripts for Environmental Monitoring on the Raspberry PI.

These feed into a MySQL database for rendering on a Grafana Dashboard. 

Not meant for production use. Just a fun side project. If you find these scripts useful, feel free to use them.


### License
Available under MIT.


### Scripts
***PiEnvironmentMonitor.py***

- Bosch BME680  (Temperature, Humidity, Pressure and VOC)
- LTR-559  (Light Sensor)
- Pi Camera (Sky Watching)

***monitor_hue.py***

- Philips Hue motion sensors contain Temperature and Light sensors in them.  This script can read those data and store it in the same MySQL Datasbase. 

***wifi_reset.sh***

 - The Raspberry Pi Zero W wifi radio is a bit flaky.  This script will reset the interface if it detects an outage. 


### Database
Schema is located in install.sql


### Thanks
[pimoroni Library and Examples ](https://github.com/pimoroni/bme680-python)



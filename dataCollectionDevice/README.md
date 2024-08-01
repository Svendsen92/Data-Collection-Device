# Data Collection Device

### *Objective*
The objective of the code in this directory is to create a small formfactor data collection device, that gathers data about the environment (temperature, humidity, light intensity, Co2, etc). The device has to be easily configurable and able to run a database, in which all device related and sensor data is stored.


### *Hardware*
The small formfactor data collection device used is a Raspberry Pi3.
  - Temperature & Humidity Sensor --> DHT11
  - Light Intensity Sensor --> Photosensitive Resistance LDR


### *How to get it running*
The Libraries required to be installed on the Raspberry Pi:
1. sudo apt update & sudo apt upgrade --> (Always do this)
2. sudo pip install Adafruit-DHT --> (Used for interacting with the temperature & humidity sensor)
3. sudo pip install mysql-connector-python --> (Used for interaction with mySQL database)
4. Used to install mariaDB on linux --> [tutorial link](https://raspberrytips.com/install-mariadb-raspberry-pi/)

<br>
Now the libraries & programs needed should be ready.

### *How to use to application*
In progress


### *To be done*
- Raspberry Pi:
  * Make a function to connect to a wifi network using SSID & Password.
  * Make webinterface prettier.




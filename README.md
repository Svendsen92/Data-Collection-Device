# Data Collection Device

### *Objective*
This repository contains sensory part of a larger project which aims to develop a small formfactor data collection device, that gathers data about the environment (temperature, humidity, light intensity, Co2, etc). The other part of the project is to create a web application, which allows multiple data collection devices to be add and their data viewed. 

The data collection device must be easily configurable and able to run a database, in which all device related and sensor data is stored.


### *Specifications*
#### Hardware
The small formfactor data collection device used is a Raspberry Pi3.
  - Temperature & Humidity Sensor --> DHT11
  - Light Intensity Sensor --> Photosensitive Resistance LDR

#### Software
- The device is configurable through a web server, which is build using the Flask framework.
- The database used is MariaDB, as it works well with an raspberry Pi.


### *How to get it running*
The Libraries required to be installed on the Raspberry Pi:
1. sudo apt update & sudo apt upgrade --> (Always do this)
2. sudo pip install Adafruit-DHT --> (Used for interacting with the temperature & humidity sensor)
3. sudo pip install mysql-connector-python --> (Used for interaction with mySQL database)
4. Used to install mariaDB on linux --> [tutorial link](https://raspberrytips.com/install-mariadb-raspberry-pi/)


The Libraries required to be installed on the computer:
1. TBD
2. TBD

<br>
Now the libraries & programs needed should be ready.

### *How to use to application*
In progress


### *To be done*
* Make a functionality that connects device to user-account to facilitate database read/write privileges.
* Make a function to connect to a wifi network using SSID & Password.
* Make web-interface prettier.


### *License* 
TBD
